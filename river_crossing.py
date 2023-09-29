import aiger

from aiger_sat import SolverWrapper

solver = SolverWrapper()  # defaults to Glucose4

TIMESTEPS = 7  # timesteps after t0, so we have one timestep more
CHARACTERS = 'w', 'g', 'c', 'f'

variables = {}
reverse_variables = {}
n_variables = 0

for character in CHARACTERS:
    for t in range(TIMESTEPS + 1):  # 0 to TIMESTEPS (incl)
        n_variables += 1
        variables[character + str(t)] = aiger.atom(character + str(t))

if __name__ == '__main__':
    # define start and goal
    init = ~variables['w0'] & ~variables['g0'] & ~variables['c0'] & ~variables['f0']
    goal = variables['w' + str(TIMESTEPS)] & variables['g' + str(TIMESTEPS)] & variables['c' + str(TIMESTEPS)] & \
           variables['f' + str(TIMESTEPS)]

    expr = init & goal

    # define illegal combinations
    for t in range(TIMESTEPS + 1):  # 0 to TIMESTEPS (incl)
        danger1 = ~((variables['w' + str(t)] == variables['g' + str(t)]) &
                    (variables['w' + str(t)] == ~variables['f' + str(t)]))
        danger2 = ~((variables['g' + str(t)] == variables['c' + str(t)]) &
                    (variables['g' + str(t)] == ~variables['f' + str(t)]))
        expr = expr & danger1 & danger2

    # define transitions
    for t in range(1, TIMESTEPS + 1):  # 1 to TIMESTEPS (incl)
        farmer_crossing = variables['f' + str(t - 1)] == ~variables['f' + str(t)]
        max_one_other_crossing = (variables['w' + str(t - 1)] == variables['w' + str(t)]) & (
                    variables['g' + str(t - 1)] == variables['g' + str(t)]) | \
                                 (variables['w' + str(t - 1)] == variables['w' + str(t)]) & (
                                             variables['c' + str(t - 1)] == variables['c' + str(t)]) | \
                                 (variables['g' + str(t - 1)] == variables['g' + str(t)]) & (
                                             variables['c' + str(t - 1)] == variables['c' + str(t)])
        expr = expr & farmer_crossing & max_one_other_crossing

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
