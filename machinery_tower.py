from cspuz import graph, Solver, count_true, BoolGridFrame
from cspuz.puzzle import util as puz_util
from util import get_direction_order, get_pathlength
from cspuz.array import BoolArray1D, IntArray1D, IntArray2D
from cspuz.constraints import count_true, fold_or, fold_and, alldifferent

def solve_arrow_maze():
    solver = Solver()
    grid = solver.int_array((4, 4), 1, 16)
    solver.add_answer_key(grid)
    solver.ensure(alldifferent(grid))
    solver.ensure(grid[0, 0] == 1)
    solver.ensure(grid[3, 3] == 16)
    solver.ensure(grid[2, 2] == 9)
    solver.ensure((grid[0, 1] - grid[0, 0] == 1) | (grid[0, 2] - grid[0, 0] == 1) |(grid[0, 3] - grid[0, 0] == 1))
    solver.ensure((grid[1, 2] - grid[0, 1] == 1) | (grid[2, 3] - grid[0, 1] == 1))
    solver.ensure((grid[0, 3] - grid[0, 2] == 1))
    solver.ensure((grid[1, 3] - grid[0, 3] == 1) | (grid[2, 3] - grid[0, 3] == 1) | (grid[3, 3] - grid[0, 3] == 1))
    solver.ensure((grid[2, 1] - grid[1, 0] == 1) | (grid[3, 2] - grid[1, 0] == 1))
    solver.ensure((grid[2, 1] - grid[1, 1] == 1) | (grid[3, 1] - grid[1, 1] == 1))
    solver.ensure((grid[1, 1] - grid[1, 2] == 1) | (grid[1, 0] - grid[1, 2] == 1))
    solver.ensure((grid[1, 2] - grid[1, 3] == 1) | (grid[1, 1] - grid[1, 3] == 1) | (grid[1, 0] - grid[1, 3] == 1))
    solver.ensure((grid[3, 0] - grid[2, 0] == 1))
    solver.ensure((grid[1, 1] - grid[2, 1] == 1) | (grid[0, 1] - grid[2, 1] == 1))
    solver.ensure((grid[2, 1] - grid[2, 2] == 1) | (grid[2, 0] - grid[2, 2] == 1))
    solver.ensure((grid[2, 2] - grid[2, 3] == 1) | (grid[2, 1] - grid[2, 3] == 1) | (grid[2, 0] - grid[2, 3] == 1))
    solver.ensure((grid[3, 1] - grid[3, 0] == 1) | (grid[3, 2] - grid[3, 0] == 1) | (grid[3, 3] - grid[3, 0] == 1))
    solver.ensure((grid[3, 2] - grid[3, 1] == 1) | (grid[3, 3] - grid[3, 1] == 1))
    solver.ensure((grid[2, 2] - grid[3, 2] == 1) | (grid[1, 2] - grid[3, 2] == 1) | (grid[0, 2] - grid[3, 2] == 1))

    is_sat = solver.solve()
    return is_sat, grid

def _main():
    is_sat, grid = solve_arrow_maze()
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(grid, dict([(None, "??")] + [(i, str(i).zfill(2)) for i in range(1, 17)])))

if __name__ == "__main__":
    _main()
