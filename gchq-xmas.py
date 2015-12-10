#!/usr/bin/python

# Copyright (c) 2015 Matthew Earl
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
# 
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
#     NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#     DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#     OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#     USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
See the following post for a description of the code:

    http://matthewearl.github.io/2015/12/10/gchq-xmas-card/

To run the script you'll need to install `pycosat`.

Invoke with:

    ./gchq-xmas.py


Modify the variables below to have the script work on other Nonogram puzzles.

"""

import pycosat


# Problem definition.

WIDTH = 25
HEIGHT = 25
ROW_RUNS = [
    [7, 3, 1, 1, 7,],
    [1, 1, 2, 2, 1, 1,],
    [1, 3, 1, 3, 1, 1, 3, 1,],
    [1, 3, 1, 1, 6, 1, 3, 1,],
    [1, 3, 1, 5, 2, 1, 3, 1,],
    [1, 1, 2, 1, 1,],
    [7, 1, 1, 1, 1, 1, 7,],
    [3, 3,],
    [1, 2, 3, 1, 1, 3, 1, 1, 2,],
    [1, 1, 3, 2, 1, 1,],
    [4, 1, 4, 2, 1, 2,],
    [1, 1, 1, 1, 1, 4, 1, 3,],
    [2, 1, 1, 1, 2, 5,],
    [3, 2, 2, 6, 3, 1,],
    [1, 9, 1, 1, 2, 1,],
    [2, 1, 2, 2, 3, 1,],
    [3, 1, 1, 1, 1, 5, 1,],
    [1, 2, 2, 5,],
    [7, 1, 2, 1, 1, 1, 3,],
    [1, 1, 2, 1, 2, 2, 1,],
    [1, 3, 1, 4, 5, 1,],
    [1, 3, 1, 3, 10, 2,],
    [1, 3, 1, 1, 6, 6,],
    [1, 1, 2, 1, 1, 2,],
    [7, 2, 1, 2, 5,],
]

COL_RUNS = [
    [7, 2, 1, 1, 7,],
    [1, 1, 2, 2, 1, 1,],
    [1, 3, 1, 3, 1, 3, 1, 3, 1,],
    [1, 3, 1, 1, 5, 1, 3, 1,],
    [1, 3, 1, 1, 4, 1, 3, 1,],
    [1, 1, 1, 2, 1, 1,],
    [7, 1, 1, 1, 1, 1, 7,],
    [1, 1, 3,],
    [2, 1, 2, 1, 8, 2, 1,],
    [2, 2, 1, 2, 1, 1, 1, 2,],
    [1, 7, 3, 2, 1,],
    [1, 2, 3, 1, 1, 1, 1, 1,],
    [4, 1, 1, 2, 6,],
    [3, 3, 1, 1, 1, 3, 1,],
    [1, 2, 5, 2, 2,],
    [2, 2, 1, 1, 1, 1, 1, 2, 1,],
    [1, 3, 3, 2, 1, 8, 1,],
    [6, 2, 1,],
    [7, 1, 4, 1, 1, 3,],
    [1, 1, 1, 1, 4,],
    [1, 3, 1, 3, 7, 1,],
    [1, 3, 1, 1, 1, 2, 1, 1, 4,],
    [1, 3, 1, 4, 3, 3,],
    [1, 1, 2, 2, 2, 6, 1,],
    [7, 1, 3, 2, 1, 1,],
]

GIVENS = [
  (3, 3), (3, 4), (3, 12), (3, 13), (3, 21),
  (8, 6), (8, 7), (8, 10), (8, 14), (8, 15), (8, 18),
  (16, 6), (16, 11), (16, 16), (16, 20),
  (21, 3), (21, 4), (21, 9), (21, 10), (21, 15), (21, 20), (21, 21),
]

assert len(COL_RUNS) >= WIDTH
assert len(ROW_RUNS) >= HEIGHT


# Utility classes and functions.

class Var(object):
    _num_vars = 0
    idx_to_var = {}

    @staticmethod
    def _add_var(var):
        Var._num_vars += 1
        idx = Var._num_vars
        Var.idx_to_var[idx] = var
        return idx

    def __init__(self, label):
        self.idx = self._add_var(self)
        self.label = label
    
    def __repr__(self):
        return "{}(idx={!r}, name={!r}".format(type(self).__name__,
                                               self.idx,
                                               self.label)

    def __str__(self):
        return self.label

class ShadedVar(Var):
    def __init__(self, row, col):
        super(ShadedVar, self).__init__("Shaded @ {}, {}".format(row, col))
        self.row = row
        self.col = col

def pretty_print_solution(sol):
    positive_indices = {t for t in sol if t > 0}
    for row in range(HEIGHT):
        print "".join(".#"[shaded_vars[row, col].idx in positive_indices]
                                                       for col in range(WIDTH))
    print


# Variable definitions.

shaded_vars = {(row, col): ShadedVar(row, col)
                              for row in range(HEIGHT) for col in range(WIDTH)}

row_run_vars = {
    (row, run_idx, start_col): Var("Row,run {},{} starts at col {}".format(
                                                      row, run_idx, start_col))
            for row in range(HEIGHT)
            for run_idx in range(len(ROW_RUNS[row]))
            for start_col in range(WIDTH)
}

col_run_vars = {
    (col, run_idx, start_row): Var("Col,run {},{} starts at row {}".format(
                                                      col, run_idx, start_row))
            for col in range(WIDTH)
            for run_idx in range(len(COL_RUNS[col]))
            for start_row in range(HEIGHT)
}


# Functions for generating clauses.

# A row run being present at a particular column implies the corresponding
# cells are shaded.
def row_run_implies_shaded():
    clauses = []
    for (row, run_idx, start_col), run_var in row_run_vars.items():
        run_len = ROW_RUNS[row][run_idx]
        for col in range(start_col,
                         min(start_col + run_len, WIDTH)):
            clauses.append([-run_var.idx, shaded_vars[row, col].idx])
    return clauses

# Similar for column runs.
def col_run_implies_shaded():
    clauses = []
    for (col, run_idx, start_row), run_var in col_run_vars.items():
        run_len = COL_RUNS[col][run_idx]
        for row in range(start_row,
                         min(start_row + run_len, HEIGHT)):
            clauses.append([-run_var.idx, shaded_vars[row, col].idx])
    return clauses

# Conversely, a cell being shaded implies a row run must exist that covers it.
def shaded_implies_row_run():
    clauses = []
    for (row, col), shaded_var in shaded_vars.items():
        clause = [-shaded_var.idx]
        for run_idx, run_len in enumerate(ROW_RUNS[row]):
            clause += [row_run_vars[row, run_idx, start_col].idx
                            for start_col in range(max(0, col - run_len + 1),
                                                   col + 1)]
        clauses.append(clause)
    return clauses

# Similarly for column runs.
def shaded_implies_col_run():
    clauses = []
    for (row, col), shaded_var in shaded_vars.items():
        clause = [-shaded_var.idx]
        for run_idx, run_len in enumerate(COL_RUNS[col]):
            clause += [col_run_vars[col, run_idx, start_row].idx
                            for start_row in range(max(0, row - run_len + 1),
                                                   row + 1)]
        clauses.append(clause)
    return clauses

# A row run being in a particular position means the next row run can't be in
# an earlier position.
def row_run_ordering():
    clauses = []
    for (row, run_idx, start_col), run_var in row_run_vars.items():
        if run_idx < len(ROW_RUNS[row]) - 1:
            first_valid_col = start_col + ROW_RUNS[row][run_idx] + 1
            for other_start_col in range(min(first_valid_col, WIDTH)):
                other_run_var = row_run_vars[row, run_idx + 1, other_start_col]
                clauses.append([-run_var.idx, -other_run_var.idx])
    return clauses

# Similarly for column runs.
def col_run_ordering():
    clauses = []
    for (col, run_idx, start_row), run_var in col_run_vars.items():
        if run_idx < len(COL_RUNS[col]) - 1:
            first_valid_row = start_row + COL_RUNS[col][run_idx] + 1
            for other_start_row in range(min(first_valid_row, HEIGHT)):
                other_run_var = col_run_vars[col, run_idx + 1, other_start_row]
                clauses.append([-run_var.idx, -other_run_var.idx])

    return clauses

# A row run can only be in at most one position.
def row_run_at_most_one_position():
    clauses = []
    for (row, run_idx, start_col), run_var in row_run_vars.items():
        for other_start_col in range(WIDTH):
            if other_start_col != start_col:
                other_run_var = row_run_vars[row, run_idx, other_start_col]
                clauses.append([-run_var.idx, -other_run_var.idx])
    return clauses

# Similarly for column runs.
def col_run_at_most_one_position():
    clauses = []
    for (col, run_idx, start_row), run_var in col_run_vars.items():
        for other_start_row in range(HEIGHT):
            if other_start_row != start_row:
                other_run_var = col_run_vars[col, run_idx, other_start_row]
                clauses.append([-run_var.idx, -other_run_var.idx])
    return clauses

# Each row run must be in at least one position.
def row_run_at_least_one_position():
    clauses = []
    for row in range(HEIGHT):
        for run_idx, run_len in enumerate(ROW_RUNS[row]):
            clause = []
            for start_col in range(WIDTH):
                clause.append(row_run_vars[row, run_idx, start_col].idx)
            clauses.append(clause)
    return clauses

# Similarly for column runs.
def col_run_at_least_one_position():
    clauses = []
    for col in range(WIDTH):
        for run_idx, run_len in enumerate(COL_RUNS[col]):
            clause = []
            for start_row in range(HEIGHT):
                clause.append(col_run_vars[col, run_idx, start_row].idx)
            clauses.append(clause)
    return clauses

# Exclude invalid row run positions.
def exclude_invalid_row_run_positions():
    clauses = []
    for row in range(HEIGHT):
        for run_idx, run_len in enumerate(ROW_RUNS[row]):
            for start_col in range(WIDTH - run_len + 1, WIDTH):
                clauses.append([-row_run_vars[row, run_idx, start_col].idx])
    return clauses

# Similarly for column runs.
def exclude_invalid_col_run_positions():
    clauses = []
    for col in range(WIDTH):
        for run_idx, run_len in enumerate(COL_RUNS[col]):
            for start_row in range(HEIGHT - run_len + 1, HEIGHT):
                clauses.append([-col_run_vars[col, run_idx, start_row].idx])
    return clauses

# Ensure the given cells are shaded.
def fix_givens():
    clauses = []
    for row, col in GIVENS:
        clauses.append([shaded_vars[row, col].idx])

    return clauses

# Put together all the clauses, and then find the results.

all_clauses = (
    row_run_implies_shaded() +
    col_run_implies_shaded() +
    shaded_implies_row_run() +
    shaded_implies_col_run() +
    row_run_ordering() +
    col_run_ordering() +
    row_run_at_most_one_position() +
    col_run_at_most_one_position() +
    row_run_at_least_one_position() +
    col_run_at_least_one_position() +
    exclude_invalid_row_run_positions() +
    exclude_invalid_col_run_positions() +
    fix_givens()
)

for sol_idx, sol in enumerate(pycosat.itersolve(all_clauses)):
    pretty_print_solution(sol)

