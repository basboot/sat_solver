import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

import aiger

from aiger_sat import SolverWrapper

solver = SolverWrapper()  # defaults to Glucose4

TRIANGLE_SIZE = 10

def draw_triangle(i, j):
    # even: pointing up, odd: pointing down. top of the triangle is always the middle of the x

    if (i + j) % 2 == 1: #odd
        plt.plot([TRIANGLE_SIZE * j, TRIANGLE_SIZE * j + TRIANGLE_SIZE //2, TRIANGLE_SIZE * j - TRIANGLE_SIZE // 2, TRIANGLE_SIZE * j],
                 [TRIANGLE_SIZE * (i + 1), TRIANGLE_SIZE * i, TRIANGLE_SIZE * i, TRIANGLE_SIZE * (i + 1)], color="grey")

    else: # even
        plt.plot([TRIANGLE_SIZE * j, TRIANGLE_SIZE * j + TRIANGLE_SIZE //2, TRIANGLE_SIZE * j - TRIANGLE_SIZE // 2, TRIANGLE_SIZE * j],
                 [TRIANGLE_SIZE * i, TRIANGLE_SIZE * (i + 1), TRIANGLE_SIZE * (i+1), TRIANGLE_SIZE * i] , color="grey")


for i in range(11):
    for j in range(43):
        draw_triangle(i, j)

plt.gca().invert_yaxis()
# plt.show()

HEIGHT = 11
WIDTH = 43

# create variables for the problem
variables = {}

for i in range(HEIGHT):
    for j in range(WIDTH):
        variables[(i, j)] = aiger.atom(f"tile_{i}_{j}")

# add constraints
def add_constraint(i, j, n):
    pass
    # set false
    # set combintations around to true and false

def add_bomb(i, j):
    pass
    # set true
    variables[(i, j)]

# set constraint on total

import itertools

for comb in itertools.combinations(variables, 122):
    #print(comb)
    pass
#
# # create dummy variable (which will result to true) to start building clauses
# DUMMY = aiger.atom('dummy')
#
# expr = DUMMY
#
# satifiable = solver.is_sat()
#
# if satifiable:
#     model = solver.get_model()
#     print("Model", model)
