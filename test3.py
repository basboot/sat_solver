# https://pysathq.github.io/docs/html/api/formula.html#pysat.formula.CNF
# https://github.com/mvcisback/py-aiger

import aiger
from pysat.solvers import Solver

a, b, c, d = aiger.atom('a'), aiger.atom('b'), aiger.atom('c'), aiger.atom('d')
expr = (a & b) | (c & d)
print(expr.aig)
from pysat.formula import CNF
cnf = CNF(from_aiger=expr.aig)
print(cnf.nv)
print(cnf.clauses)
print(['{0} <-> {1}'.format(v, cnf.vpool.obj(v)) for v in cnf.inps])
print(['{0} <-> {1}'.format(v, cnf.vpool.obj(v)) for v in cnf.outs])

# create a SAT solver for this formula:
with Solver(bootstrap_with=cnf) as solver:
    # 1.1 call the solver for this formula:
    print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

    # 1.2 the formula is satisfiable and so has a model:
    print('and the model is:', solver.get_model())

