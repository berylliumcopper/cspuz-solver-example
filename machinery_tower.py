from cspuz import graph, Solver, count_true, BoolGridFrame
from cspuz.puzzle import util as puz_util
from cspuz.graph import active_vertices_connected
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
    solver.ensure(grid[2, 2] == 4)
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

def _main1():
    is_sat, grid = solve_arrow_maze()
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(grid, dict([(None, "??")] + [(i, str(i).zfill(2)) for i in range(1, 17)])))


def solve_dice_skyscrapers():
    solver = Solver()
    grid = solver.int_array((6, 6), 1, 6)
    solver.add_answer_key(grid)
    for y in range(6):
        solver.ensure(alldifferent(grid[y, :]))
    for x in range(6):
        solver.ensure(alldifferent(grid[:, x]))
    max_left = solver.int_array((6, 6), 1, 6)
    max_right = solver.int_array((6, 6), 1, 6)
    max_up = solver.int_array((6, 6), 1, 6)
    max_down = solver.int_array((6, 6), 1, 6)
    for y in range(6):
        solver.ensure(max_left[y, 0] == grid[y, 0])
        solver.ensure(max_right[y, 5] == grid[y, 5])
        solver.ensure(max_up[0, y] == grid[0, y])
        solver.ensure(max_down[5, y] == grid[5, y])
        for x in range(1, 6):
            solver.ensure(max_left[y, x] == (max_left[y, x - 1] > grid[y, x]).cond(max_left[y, x - 1], grid[y, x]))
            solver.ensure(max_right[y, 5 - x] == (max_right[y, 5 - x + 1] > grid[y, 5 - x]).cond(max_right[y, 5 - x + 1], grid[y, 5 - x]))
            solver.ensure(max_up[x, y] == (max_up[x - 1, y] > grid[x, y]).cond(max_up[x - 1, y], grid[x, y]))
            solver.ensure(max_down[5 - x, y] == (max_down[5 - x + 1, y] > grid[5 - x, y]).cond(max_down[5 - x + 1, y], grid[5 - x, y]))
    sky_left = solver.int_array(6, 1, 6)
    sky_right = solver.int_array(6, 1, 6)
    sky_up = solver.int_array(6, 1, 6)
    sky_down = solver.int_array(6, 1, 6)
    for y in range(6):
        solver.ensure(sky_left[y] == count_true(grid[y, :] == max_left[y, :]))
        solver.ensure(sky_right[y] == count_true(grid[y, :] == max_right[y, :]))
        solver.ensure(sky_up[y] == count_true(grid[:, y] == max_up[:, y]))
        solver.ensure(sky_down[y] == count_true(grid[:, y] == max_down[:, y]))
    
    solver.ensure(sky_up[3] == 3)
    solver.ensure(grid[3, 4] == 3)

    solver.ensure(grid[0, 3] + grid[2, 1] == 7)
    solver.ensure(grid[1, 2] + grid[1, 0] == 7)
    solver.ensure(grid[1, 3] + grid[1, 1] == 7)
    solver.ensure(alldifferent([grid[0, 3], grid[2, 1], grid[1, 2], grid[1, 0], grid[1, 3], grid[1, 1]]))

    solver.ensure(grid[0, 5] + grid[2, 5] == 7)
    solver.ensure(grid[1, 5] + grid[3, 5] == 7)
    solver.ensure(grid[2, 4] + sky_right[2] == 7)
    solver.ensure(alldifferent([grid[0, 5], grid[2, 5], grid[1, 5], grid[3, 5], grid[2, 4], sky_right[2]]))

    solver.ensure(grid[2, 2] + grid[4, 3] == 7)
    solver.ensure(grid[3, 1] + grid[3, 3] == 7)
    solver.ensure(grid[3, 2] + grid[3, 4] == 7)
    solver.ensure(alldifferent([grid[2, 2], grid[4, 3], grid[3, 1], grid[3, 3], grid[3, 2], grid[3, 4]]))

    solver.ensure(grid[3, 0] + grid[5, 0] == 7)
    solver.ensure(grid[4, 0] + sky_down[0] == 7)
    solver.ensure(grid[5, 1] + sky_left[5] == 7)
    solver.ensure(alldifferent([grid[3, 0], grid[5, 0], grid[4, 0], sky_down[0], grid[5, 1], sky_left[5]]))

    is_sat = solver.solve()
    return is_sat, grid

def _main2():
    is_sat, grid = solve_dice_skyscrapers()
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(grid, dict([(None, "?")] + [(i, str(i)) for i in range(1, 7)])))


def solve_easy_as():
    solver = Solver()
    grid = solver.int_array((7, 7), 0, 4)
    solver.add_answer_key(grid)
    for y in range(7):
        for i in [1, 2, 3, 4]:
            solver.ensure(count_true([grid[y, x] == i for x in range(7)]) == 1)
    for x in range(7):
        for i in [1, 2, 3, 4]:
            solver.ensure(count_true([grid[y, x] == i for y in range(7)]) == 1)

    for y in range(7):
        for x in range(6):
            solver.ensure(((grid[y, x] != 0) & (grid[y, x + 1] != 0)).then((grid[y, x] - grid[y, x + 1] != 1) & (grid[y, x] - grid[y, x + 1] != -1)))
    for x in range(7):
        for y in range(6):
            solver.ensure(((grid[y, x] != 0) & (grid[y + 1, x] != 0)).then((grid[y, x] - grid[y + 1, x] != 1) & (grid[y, x] - grid[y + 1, x] != -1)))
    
    to_left = solver.int_array(7, 1, 4)
    to_right = solver.int_array(7, 1, 4)
    to_up = solver.int_array(7, 1, 4)
    to_down = solver.int_array(7, 1, 4)
    for y in range(7):
        solver.ensure(to_left[y] == (grid[y, 0] == 0).cond((grid[y, 1] == 0).cond((grid[y, 2] == 0).cond(grid[y, 3], grid[y, 2]), grid[y, 1]), grid[y, 0]))
        solver.ensure(to_right[y] == (grid[y, 6] == 0).cond((grid[y, 5] == 0).cond((grid[y, 4] == 0).cond(grid[y, 3], grid[y, 4]), grid[y, 5]), grid[y, 6]))
    for x in range(7):
        solver.ensure(to_up[x] == (grid[0, x] == 0).cond((grid[1, x] == 0).cond((grid[2, x] == 0).cond(grid[3, x], grid[2, x]), grid[1, x]), grid[0, x]))
        solver.ensure(to_down[x] == (grid[6, x] == 0).cond((grid[5, x] == 0).cond((grid[4, x] == 0).cond(grid[3, x], grid[4, x]), grid[5, x]), grid[6, x]))
    
    solver.ensure(to_left[0] == 3)
    solver.ensure(to_left[1] == 3)
    solver.ensure(to_left[2] == 2)
    solver.ensure(to_left[6] == 1)
    solver.ensure(to_right[0] == 4)
    solver.ensure(to_right[4] == 3)
    solver.ensure(to_right[5] == 2)
    solver.ensure(to_right[6] == 3)
    solver.ensure(to_up[0] == 2)
    solver.ensure(to_up[1] == 3)
    solver.ensure(to_up[2] == 3)
    solver.ensure(to_up[3] == 1)
    solver.ensure(to_up[4] == 1)
    solver.ensure(to_up[5] == 2)
    solver.ensure(to_up[6] == 4)
    solver.ensure(to_down[0] == 1)
    solver.ensure(to_down[1] == 4)
    solver.ensure(to_down[2] == 2)
    solver.ensure(to_down[3] == 2)
    solver.ensure(to_down[4] == 3)
    solver.ensure(to_down[5] == 3)
    solver.ensure(to_down[6] == 3)

    is_sat = solver.solve()
    return is_sat, grid

def _main3():
    is_sat, grid = solve_easy_as()
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(grid, dict([(None, "?")] + [(i, str(i)) for i in range(0, 5)])))


def solve_mathrax():
    solver = Solver()
    grid = solver.int_array((8, 8), 1, 8)
    solver.add_answer_key(grid)
    for y in range(8):
        solver.ensure(alldifferent(grid[y, :]))
    for x in range(8):
        solver.ensure(alldifferent(grid[:, x]))
    
    solver.ensure(grid[3, 5] == 5)
    solver.ensure(grid[4, 2] == 8)

    solver.ensure((grid[0, 0] == 1) | (grid[0, 0] == 3) | (grid[0, 0] == 5) | (grid[0, 0] == 7))
    solver.ensure((grid[0, 1] == 1) | (grid[0, 1] == 3) | (grid[0, 1] == 5) | (grid[0, 1] == 7))
    solver.ensure((grid[1, 0] == 1) | (grid[1, 0] == 3) | (grid[1, 0] == 5) | (grid[1, 0] == 7))
    solver.ensure((grid[1, 1] == 1) | (grid[1, 1] == 3) | (grid[1, 1] == 5) | (grid[1, 1] == 7))

    solver.ensure((grid[3, 6] == 1) | (grid[3, 6] == 3) | (grid[3, 6] == 5) | (grid[3, 6] == 7))
    solver.ensure((grid[3, 7] == 1) | (grid[3, 7] == 3) | (grid[3, 7] == 5) | (grid[3, 7] == 7))
    solver.ensure((grid[4, 6] == 1) | (grid[4, 6] == 3) | (grid[4, 6] == 5) | (grid[4, 6] == 7))
    solver.ensure((grid[4, 7] == 1) | (grid[4, 7] == 3) | (grid[4, 7] == 5) | (grid[4, 7] == 7))

    solver.ensure((grid[4, 4] == 1) | (grid[4, 4] == 3) | (grid[4, 4] == 5) | (grid[4, 4] == 7))
    solver.ensure((grid[4, 5] == 1) | (grid[4, 5] == 3) | (grid[4, 5] == 5) | (grid[4, 5] == 7))
    solver.ensure((grid[5, 4] == 1) | (grid[5, 4] == 3) | (grid[5, 4] == 5) | (grid[5, 4] == 7))
    solver.ensure((grid[5, 5] == 1) | (grid[5, 5] == 3) | (grid[5, 5] == 5) | (grid[5, 5] == 7))

    solver.ensure((grid[5, 2] == 1) | (grid[5, 2] == 3) | (grid[5, 2] == 5) | (grid[5, 2] == 7))
    solver.ensure((grid[5, 3] == 1) | (grid[5, 3] == 3) | (grid[5, 3] == 5) | (grid[5, 3] == 7))
    solver.ensure((grid[6, 2] == 1) | (grid[6, 2] == 3) | (grid[6, 2] == 5) | (grid[6, 2] == 7))
    solver.ensure((grid[6, 3] == 1) | (grid[6, 3] == 3) | (grid[6, 3] == 5) | (grid[6, 3] == 7))

    solver.ensure((grid[1, 4] == 2) | (grid[1, 4] == 4) | (grid[1, 4] == 6) | (grid[1, 4] == 8))
    solver.ensure((grid[1, 5] == 2) | (grid[1, 5] == 4) | (grid[1, 5] == 6) | (grid[1, 5] == 8))
    solver.ensure((grid[2, 4] == 2) | (grid[2, 4] == 4) | (grid[2, 4] == 6) | (grid[2, 4] == 8))
    solver.ensure((grid[2, 5] == 2) | (grid[2, 5] == 4) | (grid[2, 5] == 6) | (grid[2, 5] == 8))

    solver.ensure(grid[0, 1] + grid[1, 2] == 8)
    solver.ensure(grid[1, 1] + grid[0, 2] == 8)

    solver.ensure(grid[0, 2] + grid[1, 3] == 11)
    solver.ensure(grid[1, 2] + grid[0, 3] == 11)

    solver.ensure(grid[2, 2] + grid[3, 3] == 7)
    solver.ensure(grid[3, 2] + grid[2, 3] == 7)

    solver.ensure(grid[6, 3] + grid[7, 4] == 13)
    solver.ensure(grid[7, 3] + grid[6, 4] == 13)

    solver.ensure(grid[6, 5] + grid[7, 6] == 5)
    solver.ensure(grid[7, 5] + grid[6, 6] == 5)

    solver.ensure((grid[3, 0] - grid[4, 1] == 2) | (grid[3, 0] - grid[4, 1] == -2))
    solver.ensure((grid[3, 1] - grid[4, 0] == 2) | (grid[3, 1] - grid[4, 0] == -2))

    solver.ensure((grid[3, 3] - grid[4, 4] == 2) | (grid[3, 3] - grid[4, 4] == -2))
    solver.ensure((grid[3, 4] - grid[4, 3] == 2) | (grid[3, 4] - grid[4, 3] == -2))

    solver.ensure((grid[6, 4] - grid[7, 5] == 2) | (grid[6, 4] - grid[7, 5] == -2))
    solver.ensure((grid[6, 5] - grid[7, 4] == 2) | (grid[6, 5] - grid[7, 4] == -2))

    solver.ensure(((grid[0, 3] == 1) & (grid[1, 4] == 2)) | ((grid[0, 3] == 2) & (grid[1, 4] == 4)) | ((grid[0, 3] == 3) & (grid[1, 4] == 6)) | ((grid[0, 3] == 4) & (grid[1, 4] == 8)) | ((grid[0, 3] == 4) & (grid[1, 4] == 1)) | ((grid[0, 3] == 8) & (grid[1, 4] == 2)) | ((grid[0, 3] == 6) & (grid[1, 4] == 3)) | ((grid[0, 3] == 8) & (grid[1, 4] == 4)))

    solver.ensure(((grid[6, 6] == 1) & (grid[7, 7] == 8)) | ((grid[6, 6] == 2) & (grid[7, 7] == 4)) | ((grid[6, 6] == 4) & (grid[7, 7] == 2)) | ((grid[6, 6] == 8) & (grid[7, 7] == 1)))
    solver.ensure(((grid[6, 7] == 1) & (grid[7, 6] == 8)) | ((grid[6, 7] == 2) & (grid[7, 6] == 4)) | ((grid[6, 7] == 4) & (grid[7, 6] == 2)) | ((grid[6, 7] == 8) & (grid[7, 6] == 1)))


    is_sat = solver.solve()
    return is_sat, grid

def _main4():
    is_sat, grid = solve_mathrax()
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(grid, dict([(None, "?")] + [(i, str(i)) for i in range(1, 9)])))


def solve_kurodoko():
    solver = Solver()
    grid = solver.bool_array((11, 11))
    solver.add_answer_key(grid)
    for y in range(11):
        for x in range(10):
            solver.ensure(grid[y, x] | grid[y, x + 1])
    for x in range(11):
        for y in range(10):
            solver.ensure(grid[y, x] | grid[y + 1, x])
    

    active_vertices_connected(solver, grid)

    to_left = solver.int_array((11, 11), 0, 11)
    to_right = solver.int_array((11, 11), 0, 11)
    to_up = solver.int_array((11, 11), 0, 11)
    to_down = solver.int_array((11, 11), 0, 11)
    for y in range(11):
        solver.ensure(to_left[y, 0] == (grid[y, 0].cond(1, 0)))
        for x in range(10):
            solver.ensure(to_left[y, x + 1] == (grid[y, x + 1].cond(to_left[y, x] + 1, 0)))
        solver.ensure(to_right[y, 10] == (grid[y, 10].cond(1, 0)))
        for x in range(10):
            solver.ensure(to_right[y, x] == (grid[y, x].cond(to_right[y, x + 1] + 1, 0)))
    for x in range(11):
        solver.ensure(to_up[0, x] == (grid[0, x].cond(1, 0)))
        for y in range(10):
            solver.ensure(to_up[y + 1, x] == (grid[y + 1, x].cond(to_up[y, x] + 1, 0)))
        solver.ensure(to_down[10, x] == (grid[10, x].cond(1, 0)))
        for y in range(10):
            solver.ensure(to_down[y, x] == (grid[y, x].cond(to_down[y + 1, x] + 1, 0)))
    
    numbers = [(0, 0, 2), (0, 3, 2), (0, 6, 2), (0, 10, 2), (1, 1, 3), (1, 5, 2), (2, 2, 4), (2, 10, 4), (3, 1, 2), (4, 2, 2), (4, 4, 5), (4, 7, 6), (5, 9, 6), (6, 3, 5), (6, 6, 8), (6, 8, 7), (8, 0, 5), (8, 4, 7), (8, 8, 9), (9, 9, 3), (10, 0, 2), (10, 4, 2), (10, 7, 2), (10, 10, 2)]
    for y, x, n in numbers:
        solver.ensure(to_left[y, x] + to_right[y, x] + to_up[y, x] + to_down[y, x] == n + 3)

    is_sat = solver.solve()
    return is_sat, grid

def _main5():
    is_sat, grid = solve_kurodoko()
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(grid, dict([(None, "?"), (True, "."), (False, "X")])))

if __name__ == "__main__":
    _main1()
