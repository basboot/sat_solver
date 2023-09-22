from pysat.formula import CNF

cnf = CNF(from_clauses=[[-1, 2], [-1, -2]])

cnf.append([3, 4])
print(cnf.clauses)


# True
# [-1, -2, -3]