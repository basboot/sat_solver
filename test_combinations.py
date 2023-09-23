import itertools
from pysat.solvers import Solver
from pysat.formula import CNF


POSITIONS = list("01234567")
VALUES = list("0123456789")

# 59140052
guesses = [
    ("68076675", 0),
    ("41639532", 1),
    ("19098806", 1),
    ("88045343", 1),
    ("52698367", 1),
    ("40429823", 0),
    ("19440636", 3),
    ("87429843", 0),
    ("92075423", 0),
    ("15371510", 0),
]

# POSITIONS = list("012")
# VALUES = list("01")
#
# guesses = [
#     # ("011", 2),
#     ("110", 2),
#     # ("100", 1),
#     ("010", 1),
#     ("001", 1),
# ]

# POSITIONS = list("0123")
# VALUES = list("012")
#
# # 3020
# guesses = [
#     ("1222", 1),
#     ("2122", 1),
#     ("2212", 1),
#     ("2221", 1),
# ]


variables = {}
reverse_variables = {}
n_variables = 0
n_initial_variables = 0
for pos in POSITIONS:
    for val in VALUES:
        n_variables+=1
        variables[pos + val] = n_variables
        reverse_variables[n_variables] = "X_" + pos + val
        reverse_variables[-n_variables] = "~X_" + pos + val
n_initial_variables = n_variables

def create_new_variable():
    global n_variables
    global variables
    global reverse_variables

    n_variables += 1
    variables["helper" + str(n_variables)] = n_variables
    reverse_variables[n_variables] = "helper_" + str(n_variables)
    reverse_variables[-n_variables] = "~helper_" + str(n_variables)

    return n_variables


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

    show_clauses(upperbound_clauses)

    return upperbound_clauses

def dnf_2_cnf_distributive(dnf_clauses):
    dnf_product = itertools.product(*dnf_clauses)

    dnf_clauses = []
    for clause in dnf_product:
        dnf_clauses.append(clause)

    return dnf_clauses

def dnf_2_cnf(dnf_clauses):
    # convert to cnf by introducing a new variable for each conjunction clause in dnf clause
    # new_var <-> (conjunction), which can be translated to cnf as:
    # each part of conjunction must be true, or not new_var (clause's below)
    # new var must be true, or not a part of the conjuction (final_clause below)
    # one of the conjunctions must be true, so one of the new vars (overall_clause below)

    cnf_clauses = []
    overall_clause = []
    for dnf_clause in dnf_clauses:
        # create helper var
        # TODO: move to function
        helper = create_new_variable()
        # n_variables is the latest var, so this is the helper var
        final_clause = [helper]
        overall_clause.append(helper)
        for var in dnf_clause:
            final_clause.append(-var)

            clause = [-helper]
            clause.append(var)

            cnf_clauses.append(clause)

        cnf_clauses.append(final_clause)

    cnf_clauses.append(overall_clause)

    return cnf_clauses

def get_lowerbound_clauses(guess, correct):
    # define lowerbound >= correct, als dnf
    lowerbound_clauses_dnf = []
    lowerbound_combinations = itertools.combinations(guess, correct)
    for combination in lowerbound_combinations:
        clause = []
        for variable_name in combination:
            clause.append(variables[variable_name])
        lowerbound_clauses_dnf.append(clause)

    #show_clauses(lowerbound_clauses_dnf, cnf=False)

    lowerbound_clauses = dnf_2_cnf(lowerbound_clauses_dnf)

    show_clauses(lowerbound_clauses)

    return lowerbound_clauses

if __name__ == '__main__':

    # print(variables)
    #
    # dnf_tst = [[1, 2], [3, 4]]
    # show_clauses(dnf_tst, cnf=False)
    #
    # show_clauses(dnf_2_cnf_distributive(dnf_tst))
    # show_clauses(dnf_2_cnf_new(dnf_tst))
    #
    #
    # exit()
    # guess = ['01', '11', '20']
    cnf = CNF()


    # initial constrainsts: numbers must be unique

    # one value must be true for each position
    variables_positions = []
    for pos in POSITIONS:
        clause = []
        vars = []
        for value in VALUES:
            clause.append(variables[pos + value])
            vars.append(variables[pos + value])
        cnf.append(clause)
        variables_positions.append(vars)

    # no more than one can be true

    # TODO: create combination of 2 per position
    for var_pos in variables_positions:
        for illegal_combnation in itertools.combinations(var_pos, 2):
            clause = []
            for illegal_var in illegal_combnation:
                clause.append(-illegal_var)
            cnf.append(clause)


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

        with Solver(bootstrap_with=cnf) as solver:
            # 1.1 call the solver for this formula:
            print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

            # 1.2 the formula is satisfiable and so has a model:
            print('and the model is:', solver.get_model())

            negated_solution = []
            for value in solver.get_model():
                if 0 < value < n_initial_variables + 1:
                    negated_solution.append(-value)
                    print(reverse_variables[value])

            # check for uniqueness
            cnf_alternative = cnf.copy()
            cnf_alternative.append(negated_solution)
            with Solver(bootstrap_with=cnf_alternative) as solver_alternative:
                print('solution is', "not" if solver_alternative.solve() else "", "unique")





