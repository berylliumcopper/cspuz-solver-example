from cspuz import graph, Solver, count_true, BoolGridFrame
from cspuz.puzzle import util as puz_util
from util import get_direction_order, get_pathlength
from cspuz.constraints import fold_or

def solve_maze1(height, width, blocks, walls_h, walls_v, numbers, start, end):
    solver = Solver()
    grid = BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(grid)
    is_passed = graph.active_edges_single_path(solver, grid)
    for y, x in blocks:
        solver.ensure(~is_passed[y, x])
    for y, x in walls_h:
        solver.ensure(~grid.horizontal[y, x])
    for y, x in walls_v:
        solver.ensure(~grid.vertical[y, x])
    solver.ensure(count_true(grid.vertex_neighbors(start)) == 1)
    solver.ensure(count_true(grid.vertex_neighbors(end)) == 1)
    for y, x, n in numbers:
        neighbors = []
        if y > 0:
            neighbors.append(is_passed[y - 1, x])
        if y < height - 1:
            neighbors.append(is_passed[y + 1, x])
        if x > 0:
            neighbors.append(is_passed[y, x - 1])
        if x < width - 1:
            neighbors.append(is_passed[y, x + 1])
        if y > 0 and x > 0:
            neighbors.append(is_passed[y - 1, x - 1])
        if y > 0 and x < width - 1:
            neighbors.append(is_passed[y - 1, x + 1])
        if y < height - 1 and x > 0:
            neighbors.append(is_passed[y + 1, x - 1])
        if y < height - 1 and x < width - 1:
            neighbors.append(is_passed[y + 1, x + 1])
        solver.ensure(count_true(neighbors) == n)

    grid_rd, grid_lu, order_array = get_direction_order(solver, grid, is_passed, height, width, start, end)
    is_sat = solver.solve()
    return is_sat, grid, order_array

def _main1():
    height = 14
    width = 14
    blocks = [(1, 1), (1, 5), (1, 12), (3, 3), (3, 10), (5, 1), (5, 5), (5, 8), (7, 0), (7, 8), (8, 11), (9, 0), (9, 12), (11, 10), (11, 13), (13, 3), (0, 6), (1, 13), (9, 4)]
    walls_h = [(0, 2), (3, 7), (4, 3), (4, 12), (5, 6), (6, 6), (6, 7), (6, 12)]
    walls_v = [(0, 3), (1, 7), (2, 4), (2, 6), (2, 13), (3, 7), (5, 0), (6, 2)]
    numbers = [(1, 3, 6), (1, 7, 7), (1, 10, 0), (2, 12, 3), (3, 1, 1), (3, 5, 4), (3, 12, 5), (5, 10, 1), (5, 12, 6), (7, 7, 3), (8, 3, 2), (8, 5, 0), (8, 10, 7), (8, 12, 6), (9, 1, 2), (9, 3, 0), (9, 6, 2), (10, 1, 2), (11, 5, 2), (11, 6, 2), (11, 7, 2), (12, 1, 6), (13, 8, 0), (13, 13, 1)]
    start = (0, 5)
    end = (6, 3)
    is_sat, grid, order_array = solve_maze1(height, width, blocks, walls_h, walls_v, numbers, start, end)
    print("maze 1:", is_sat)
    if is_sat:
        print("grid:")
        print(puz_util.stringify_grid_frame(grid))
        print("order_array:")
        print(puz_util.stringify_array(order_array, lambda x: "XXX" if x == -1 else "???" if x == None else str(x).zfill(3)))


def solve_maze2(height, width, blocks, walls_h, walls_v, reds, whites, start, end):
    solver = Solver()
    grid = BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(grid)
    is_passed = graph.active_edges_single_path(solver, grid)
    for y, x in blocks:
        solver.ensure(~is_passed[y, x])
    for y, x in walls_h:
        solver.ensure(~grid.horizontal[y, x])
    for y, x in walls_v:
        solver.ensure(~grid.vertical[y, x])
    solver.ensure(count_true(grid.vertex_neighbors(start)) == 1)
    solver.ensure(count_true(grid.vertex_neighbors(end)) == 1)
    
    to_up, to_down, to_left, to_right = get_pathlength(solver, grid, height, width)
    grid_rd, grid_lu, order_array = get_direction_order(solver, grid, is_passed, height, width, start, end)

    for y, x in reds:
        solver.ensure(is_passed[y, x])
        conditions = []
        if x > 0 and y > 0:
            conditions.append((grid_rd.vertical[y-1,x]) & (grid_lu.horizontal[y,x-1]) & (to_up[y,x] + 2 == to_left[y,x]))
            conditions.append((grid_lu.vertical[y-1,x]) & (grid_rd.horizontal[y,x-1]) & (to_up[y,x] == to_left[y,x] + 2))
        if x < width - 1 and y > 0:
            conditions.append((grid_rd.vertical[y-1,x]) & (grid_rd.horizontal[y,x]) & (to_up[y,x] + 2 == to_right[y,x]))
            conditions.append((grid_lu.vertical[y-1,x]) & (grid_lu.horizontal[y,x]) & (to_up[y,x] == to_right[y,x] + 2))
        if x > 0 and y < height - 1:
            conditions.append((grid_lu.vertical[y,x]) & (grid_lu.horizontal[y,x-1]) & (to_down[y,x] + 2 == to_left[y,x]))
            conditions.append((grid_rd.vertical[y,x]) & (grid_rd.horizontal[y,x-1]) & (to_down[y,x] == to_left[y,x] + 2))
        if x < width - 1 and y < height - 1:
            conditions.append((grid_lu.vertical[y,x]) & (grid_rd.horizontal[y,x]) & (to_down[y,x] + 2 == to_right[y,x]))
            conditions.append((grid_rd.vertical[y,x]) & (grid_lu.horizontal[y,x]) & (to_down[y,x] == to_right[y,x] + 2))
        solver.ensure(fold_or(conditions))
    for y, x in whites:
        solver.ensure(is_passed[y, x])
        solver.ensure(to_up[y, x] == to_down[y, x])
        solver.ensure(to_left[y, x] == to_right[y, x])

    is_sat = solver.solve()
    return is_sat, grid, order_array

def _main2():
    height = 14
    width = 14
    blocks = [(1, 0), (9, 10), (11, 0), (0, 3), (7, 9), (13, 0)]
    walls_h = [(4, 5), (4, 11), (7, 3), (7, 4), (7, 5), (8, 4), (9, 11), (10, 0), (10, 6), (10, 11), (11, 8), (12, 6)]
    walls_v = [(0, 6), (1, 11), (2, 3), (2, 4), (4, 3), (4, 4), (5, 8), (5, 12), (7, 4), (8, 4), (10, 7), (11, 2), (11, 3), (11, 4), (11, 6), (11, 8), (12, 3)]
    reds = [(2, 5), (2, 7), (4, 5), (4, 7), (4, 11), (7, 2), (10, 6), (13, 1)]
    whites = [(1, 2), (2, 12), (2, 13), (5, 0), (5, 1), (5, 2), (8, 13), (10, 10), (10, 12), (11, 10), (12, 12)]
    start = (2, 11)
    end = (11, 2)
    is_sat, grid, order_array = solve_maze2(height, width, blocks, walls_h, walls_v, reds, whites, start, end)
    print("maze 2:", is_sat)
    if is_sat:
        print("grid:")
        print(puz_util.stringify_grid_frame(grid))
        print("order_array:")
        print(puz_util.stringify_array(order_array, lambda x: "XXX" if x == -1 else "???" if x == None else str(x).zfill(3)))

if __name__ == "__main__":
    _main2()