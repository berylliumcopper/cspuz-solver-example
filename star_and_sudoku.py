import sys
import subprocess

from cspuz import Solver
from cspuz.constraints import alldifferent, count_true, fold_or, fold_and
from cspuz.puzzle import util


def solve(problem):
    size = 9
    solver = Solver()
    sudoku_answer = solver.int_array((size, size), 1, size)
    solver.add_answer_key(sudoku_answer)
    star_answer = solver.bool_array((size, size))
    solver.add_answer_key(star_answer)
    for i in range(size):
        solver.ensure(alldifferent(sudoku_answer[i, :]))
        solver.ensure(alldifferent(sudoku_answer[:, i]))
        solver.ensure(count_true(star_answer[i, :]) == 1)
        solver.ensure(count_true(star_answer[:, i]) == 1)
    for y in range(3):
        for x in range(3):
            solver.ensure(alldifferent(sudoku_answer[y * 3 : (y + 1) * 3, x * 3 : (x + 1) * 3]))
            solver.ensure(count_true(star_answer[y * 3 : (y + 1) * 3, x * 3 : (x + 1) * 3]) == 1)
    for i in problem:
        (tot, cells) = i
        accumulator = solver.int_array((len(cells) + 1,), 0, 50)
        solver.ensure(accumulator[0] == 0)
        for idx, (y, x) in enumerate(cells):
            solver.ensure(accumulator[idx + 1] == accumulator[idx] + star_answer[y, x].cond(sudoku_answer[y, x] + sudoku_answer[y, x], sudoku_answer[y, x]))
        solver.ensure(accumulator[len(cells)] == tot)
    is_sat = solver.solve()

    return is_sat, sudoku_answer, star_answer


def _main():
    problem = [
        [24, [(0,0), (0,1), (1,0)]],
        [14, [(0,2), (1,1), (1,2)]],
        [9, [(2,0), (2,1), (2,2)]],
        [24, [(0,3), (1,3), (2,3)]],
        [19, [(0,4), (1,4), (2,4)]],
        [10, [(0,5), (1,5), (2,5)]],
        [13, [(0,6), (1,6), (1,7)]],
        [15, [(0,7), (0,8), (1,8)]],
        [20, [(2,6), (2,7), (2,8)]],
        [7, [(3,0), (4,0)]],
        [16, [(3,1), (3,2), (4,1)]],
        [15, [(3,3), (4,2), (4,3)]],
        [8, [(3,4)]],
        [20, [(3,5), (4,5), (4,6)]],
        [7, [(3,6), (3,7), (4,7)]],
        [19, [(3,8), (4,8)]],
        [13, [(5,0), (6,0)]],
        [3, [(5,1), (6,1)]],
        [15, [(5,2), (6,2)]],
        [6, [(5,3)]],
        [6, [(4,4), (5,4)]],
        [8, [(5,5)]],
        [9, [(5,6), (6,6)]],
        [13, [(5,7), (6,7)]],
        [12, [(5,8), (6,8)]],
        [24, [(7,0), (8,0), (8,1)]],
        [11, [(7,1), (7,2)]],
        [5, [(8,2)]],
        [14, [(6,3), (7,3), (8,3)]],
        [19, [(6,4), (7,4), (8,4)]],
        [19, [(6,5), (7,5), (8,5)]],
        [15, [(7,6), (7,7)]],
        [16, [(7,8), (8,7), (8,8)]],
        [2, [(8,6)]]
    ]
    is_sat, sudoku_answer, star_answer = solve(problem)
    if is_sat:
        print(
            util.stringify_array(
                sudoku_answer, dict([(None, "?")] + [(i, str(i)) for i in range(1, 10)])
            )
        )
        print(util.stringify_array(star_answer, {None: "?", True: "*", False: "."}))


if __name__ == "__main__":
    _main()