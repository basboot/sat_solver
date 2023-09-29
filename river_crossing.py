import aiger

from aiger_sat import SolverWrapper

import itertools

solver = SolverWrapper()  # defaults to Glucose4

TIMESTEPS = 7  # timesteps after t0, so we have one timestep more
CHARACTERS = ['w', 'g', 'c', 'f']

# dangerous character, is dangerous for characters, if not protected by character
DANGER = [('w', ['g'], 'f'), ('g', ['c'], 'f')]
BOAT_OPERATORS = ['f']
BOAT_SIZE = 2

DUMMY = aiger.atom('dummy')

variables = {}
reverse_variables = {}
n_variables = 0

for character in CHARACTERS:
    for t in range(TIMESTEPS + 1):  # 0 to TIMESTEPS (incl)
        n_variables += 1
        variables[character + str(t)] = aiger.atom(character + str(t))

if __name__ == '__main__':
    # define start and goal
    # start with something undefined to combine the conjuction
    init = DUMMY
    for character in CHARACTERS:
        init = init & ~variables[character + '0']

    # start with something undefined to combine the conjuction
    goal = DUMMY
    for character in CHARACTERS:
        goal = goal & variables[character + str(TIMESTEPS)]

    expr = init & goal

    # define illegal combinations
    for t in range(TIMESTEPS + 1):  # 0 to TIMESTEPS (incl)
        for danger in DANGER:
            dangerous_character = danger[0]
            vulnerable_characters = danger[1]
            protecting_character = danger[2]

            # start with a contradiction to combine the disjunction
            danger_clause = DUMMY == ~DUMMY
            for vulnerable_character in vulnerable_characters:
                danger_clause = danger_clause | (variables[dangerous_character + str(t)] == variables[vulnerable_character + str(t)])

            danger_clause = danger_clause & (variables[dangerous_character + str(t)] == ~variables[protecting_character + str(t)])

            expr = expr & ~danger_clause

    # define transitions
    for t in range(1, TIMESTEPS + 1):  # 1 to TIMESTEPS (incl)
        # at least one boat operator must cross
        # start with a contradiction to combine the disjunction
        operator_crossing = DUMMY == ~DUMMY
        for boat_operator in BOAT_OPERATORS:
            operator_crossing = operator_crossing | (variables[boat_operator + str(t - 1)] == ~variables[boat_operator + str(t)])


        # max two total crossing
        upperbound_combinations = itertools.combinations(CHARACTERS, BOAT_SIZE + 1)
        max_boat_size_crossings = DUMMY
        for combination in upperbound_combinations:
            too_large_crossing = DUMMY
            for character in combination:
                too_large_crossing = too_large_crossing & (variables[character + str(t - 1)] == ~variables[character + str(t)])
            max_boat_size_crossings = max_boat_size_crossings & ~too_large_crossing

        expr = expr & operator_crossing & max_boat_size_crossings

    solver.add_expr(expr)

    satifiable = solver.is_sat()

    if satifiable:
        model = solver.get_model()
        print("Model", model)

        for t in range(TIMESTEPS + 1):
            print(f"t = {t}: ", end='')
            for character in CHARACTERS:
                # 0 to TIMESTEPS (incl)
                if not model[character + str(t)]:
                    print(f"{character} ", end='')
                else:
                    print(f"  ", end='')

            print(f"| ", end='')
            for character in CHARACTERS:
                # 0 to TIMESTEPS (incl)
                if model[character + str(t)]:
                    print(f"{character} ", end='')
                else:
                    print(f"  ", end='')

            print()
    else:
        print("Problem is not satisfiable.")
