import sys

import aiger

from aiger_sat import SolverWrapper

import itertools

sys.setrecursionlimit(100000)


solver = SolverWrapper()  # defaults to Glucose4

# traditional river crossing
# TIMESTEPS = 7  # timesteps after t0, so we have one timestep more
# CHARACTERS = ['w', 'g', 'c', 'f']
#
# # dangerous character, is dangerous for characters, if not protected by character
# DANGER = [('w', ['g'], 'f'), ('g', ['c'], 'f')]
# BOAT_OPERATORS = ['f']
# BOAT_SIZE = 2

# 17 is possible
TIMESTEPS = 17  # timesteps after t0, so we have one timestep more
CHARACTERS = ['c', 'p', 'f', 'm', 'b1', 'b2', 'g1', 'g2']

# dangerous character, is dangerous for characters, if not protected by character
DANGER = [('c', ['f', 'm', 'b1', 'b2', 'g1', 'g2'], 'p'), ('f', ['g1', 'g2'], 'm'), ('m', ['b1', 'b2'], 'f')]

BOAT_OPERATORS = ['p', 'f', 'm']
BOAT_SIZE = 2



# create dummy variable (which will result to true) to start building clauses
DUMMY = aiger.atom('dummy')

# create variables for the problem
variables = {}
reverse_variables = {}
n_variables = 0

for character in CHARACTERS + ['boat']:
    for t in range(TIMESTEPS + 1):  # 0 to TIMESTEPS (incl)
        n_variables += 1
        variables[character + str(t)] = aiger.atom(character + str(t))

if __name__ == '__main__':
    # define start and goal
    # start with dummy variable to combine the conjuction
    init = DUMMY
    for character in CHARACTERS + ['boat']:
        init = init & ~variables[character + '0']

    # start with dummy variable to combine the conjuction
    goal = DUMMY
    for character in CHARACTERS + ['boat']:
        goal = goal & variables[character + str(TIMESTEPS)]

    expr = init & goal

    # define dangerous (illegal) combinations
    for t in range(TIMESTEPS + 1):  # 0 to TIMESTEPS (incl)
        for danger in DANGER:
            dangerous_character = danger[0]
            vulnerable_characters = danger[1]
            protecting_character = danger[2]

            # start with a contradiction to combine the disjunction
            danger_clause = DUMMY == ~DUMMY
            for vulnerable_character in vulnerable_characters:
                # any vulnerable_character is together with dangerous_character
                danger_clause = danger_clause | (variables[dangerous_character + str(t)] == variables[vulnerable_character + str(t)])
            # without protecting_character
            danger_clause = danger_clause & (variables[dangerous_character + str(t)] == ~variables[protecting_character + str(t)])

            # is NOT allowed
            expr = expr & ~danger_clause

    # define transitions
    for t in range(1, TIMESTEPS + 1):  # 1 to TIMESTEPS (incl)
        # boat always crosses, so it cannot be at the same side the next timestep
        boat_crosses = (variables['boat' + str(t - 1)] == ~variables['boat' + str(t)])

        # at least one boat operator must cross (cannot be at the same side)
        # start with a contradiction to combine the disjunction
        operator_crossing = DUMMY == ~DUMMY
        for boat_operator in BOAT_OPERATORS:
            operator_crossing = operator_crossing | (variables[boat_operator + str(t - 1)] == ~variables[boat_operator + str(t)])

        # max boat size total crossings (more than BOATS_SIZE + 1 cannot change sides)
        upperbound_combinations = itertools.combinations(CHARACTERS, BOAT_SIZE + 1)
        max_boat_size_crossings = DUMMY
        for combination in upperbound_combinations:
            too_large_crossing = DUMMY
            for character in combination:
                too_large_crossing = too_large_crossing & (variables[character + str(t - 1)] == ~variables[character + str(t)])
            max_boat_size_crossings = max_boat_size_crossings & ~too_large_crossing

        # crossings can only be in the direction of the boat (change side at time t must be at same as the boat variable)
        legal_crossings = DUMMY
        for character in CHARACTERS:
            with_boat = (variables[character + str(t)] == variables['boat' + str(t)])
            crossing = (variables[character + str(t - 1)] == ~variables[character + str(t)])
            legal_crossings = legal_crossings & crossing.implies(with_boat)

        # combine all constraints for this timestep, and add them to the problem
        expr = expr & boat_crosses & operator_crossing & max_boat_size_crossings & legal_crossings

    solver.add_expr(expr)

    satifiable = solver.is_sat()

    if satifiable:
        model = solver.get_model()
        print("Model", model)

        for t in range(TIMESTEPS + 1):
            print(f"t = {t}{' ' if t < 10 else ''}{' ' if t < 100 else ''}: ", end='')
            for character in CHARACTERS:
                # 0 to TIMESTEPS (incl)
                if not model[character + str(t)]:
                    print(f"{character} ", end='')
                    if len(character) < 2:
                        print(f" ", end='')
                else:
                    print(f"   ", end='')

            print(f"| ", end='')
            for character in CHARACTERS:
                # 0 to TIMESTEPS (incl)
                if model[character + str(t)]:
                    print(f"{character} ", end='')
                    if len(character) < 2:
                        print(f" ", end='')
                else:
                    print(f"   ", end='')

            print()
    else:
        print("Problem is not satisfiable.")
