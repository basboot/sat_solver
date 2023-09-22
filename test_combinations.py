import itertools
from pysat.solvers import Solver
from pysat.formula import CNF

POSITIONS = list("012")
VALUES = list("01")

# guesses = [
#     ("68076675", 0),
#     ("41639532", 1),
#     ("19098806", 1),
#     ("88045343", 1),
# 52698367 1 goed
# 40429823 0 goed
# 19440636 3 goed
# 87429843 0 goed
# 92075423 0 goed
# 15371510 0 goed
# ]

guesses = [
    ("100", 1),
    ("010", 1),
    ("001", 1),
]


variables = {}
reverse_variables = {}
n_variables = 0
for pos in POSITIONS:
    for val in VALUES:
        n_variables+=1
        variables[pos + val] = n_variables
        reverse_variables[n_variables] = "X_" + pos + val
        reverse_variables[-n_variables] = "~X_" + pos + val


def show_clauses(clauses, cnf=True):
    for i in range(len(clauses)):
        print("(", end='')
        for j in range(len(clauses[i])):
            print(reverse_variables[clauses[i][j]], end='')
            if j < len(clauses[i]) - 1:
                print(" \\/ " if cnf else " /\\ ", end='')
        print(")", end='')
        if i < len(clauses) - 1:
            print(" /\\ " if cnf else " \\/ ", end='')
    print()

def get_upperbound_clauses(guess, correct):
    # define upper bound <= correct
    upperbound_combinations = itertools.combinations(guess, correct + 1)

    upperbound_clauses = []
    for combination in upperbound_combinations:
        clause = []
        for variable_name in combination:
            clause.append(-variables[variable_name])
        upperbound_clauses.append(clause)

    print(upperbound_clauses)
    show_clauses(upperbound_clauses)

    return upperbound_clauses

def get_lowerbound_clauses(guess, correct):
    # define lowerbound >= correct, als dnf
    lowerbound_clauses_dnf = []
    lowerbound_combinations = itertools.combinations(guess, correct)
    for combination in lowerbound_combinations:
        clause = []
        for variable_name in combination:
            clause.append(variables[variable_name])
        lowerbound_clauses_dnf.append(clause)

    print(lowerbound_clauses_dnf)
    show_clauses(lowerbound_clauses_dnf, cnf=False)

    lowerbound_product = itertools.product(*lowerbound_clauses_dnf)

    lowerbound_clauses = []
    for clause in lowerbound_product:
        lowerbound_clauses.append(clause)

    print(lowerbound_clauses)
    show_clauses(lowerbound_clauses)

    return lowerbound_clauses

if __name__ == '__main__':
    # guess = ['01', '11', '20']
    cnf = CNF()

    for turn in guesses:
        print("--------------")
        print(turn)
        guess_values = list(turn[0])
        guess = []
        for i in range(len(guess_values)):
            guess.append(POSITIONS[i] + guess_values[i])
        correct = turn[1]

        assert correct < len(POSITIONS), "answer found, stop"

        upperbound_clauses = get_upperbound_clauses(guess, correct)
        lowerbound_clauses = get_lowerbound_clauses(guess, correct)

        for clause in upperbound_clauses + lowerbound_clauses:
            cnf.append(clause)

        print("clauses", cnf.clauses)


        with Solver(bootstrap_with=cnf) as solver:
            # 1.1 call the solver for this formula:
            print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

            # 1.2 the formula is satisfiable and so has a model:
            print('and the model is:', solver.get_model())

            for value in solver.get_model():
                if value > 0:
                    print(reverse_variables[value])


# TODO: toevoegen dat er maar 1 waar mag/moet zijn per positie





