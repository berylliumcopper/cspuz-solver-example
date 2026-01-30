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


def solve_maze3(height, width, walls_h, walls_v, blacks, reds, whites, letters, start, end):
    solver = Solver()
    grid = BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(grid)
    is_passed = graph.active_edges_single_path(solver, grid)
    for y, x in walls_h:
        solver.ensure(~grid.horizontal[y, x])
    for y, x in walls_v:
        solver.ensure(~grid.vertical[y, x])

    for y in range(height):
        for x in range(width):
            solver.ensure(is_passed[y, x])
    solver.ensure(count_true(grid.vertex_neighbors(start)) == 1)
    solver.ensure(count_true(grid.vertex_neighbors(end)) == 1)

    grid_rd, grid_lu, order_array = get_direction_order(solver, grid, is_passed, height, width, start, end)

    for y, x in blacks:
        name = "BLACK"
        moves = solver.int_array(len(name), 0, 3)
        curr_y, curr_x = y, x
        for i in range(len(name)):
            curr_y, curr_x = curr_y + ((moves[i] == 0) | (moves[i] == 1)).cond(0, (moves[i] == 2).cond(-1, 1)), curr_x + ((moves[i] == 2) | (moves[i] == 3)).cond(0, (moves[i] == 0).cond(-1, 1))
            conditions = []
            for sy, sx in letters[name[i]]:
                conditions.append((curr_y == sy) & (curr_x == sx) & (((grid_lu.horizontal[sy, sx] & (moves[i] == 0)) if sx < width - 1 else False) | ((grid_rd.horizontal[sy, sx-1] & (moves[i] == 1)) if sx > 0 else False) | ((grid_lu.vertical[sy, sx] & (moves[i] == 2)) if sy < height - 1 else False) | ((grid_rd.vertical[sy-1, sx] & (moves[i] == 3)) if sy > 0 else False)))
            solver.ensure(fold_or(conditions))
    
    for y, x in reds:
        name = "RED"
        moves = solver.int_array(len(name), 0, 3)
        curr_y, curr_x = y, x
        for i in range(len(name)):
            curr_y, curr_x = curr_y + ((moves[i] == 0) | (moves[i] == 1)).cond(0, (moves[i] == 2).cond(-1, 1)), curr_x + ((moves[i] == 2) | (moves[i] == 3)).cond(0, (moves[i] == 0).cond(-1, 1))
            conditions = []
            for sy, sx in letters[name[i]]:
                conditions.append((curr_y == sy) & (curr_x == sx) & (((grid_lu.horizontal[sy, sx] & (moves[i] == 0)) if sx < width - 1 else False) | ((grid_rd.horizontal[sy, sx-1] & (moves[i] == 1)) if sx > 0 else False) | ((grid_lu.vertical[sy, sx] & (moves[i] == 2)) if sy < height - 1 else False) | ((grid_rd.vertical[sy-1, sx] & (moves[i] == 3)) if sy > 0 else False)))
            solver.ensure(fold_or(conditions))

    for y, x in whites:
        name = "WHITE"
        moves = solver.int_array(len(name), 0, 3)
        curr_y, curr_x = y, x
        for i in range(len(name)):
            curr_y, curr_x = curr_y + ((moves[i] == 0) | (moves[i] == 1)).cond(0, (moves[i] == 2).cond(-1, 1)), curr_x + ((moves[i] == 2) | (moves[i] == 3)).cond(0, (moves[i] == 0).cond(-1, 1))
            conditions = []
            for sy, sx in letters[name[i]]:
                conditions.append((curr_y == sy) & (curr_x == sx) & (((grid_lu.horizontal[sy, sx] & (moves[i] == 0)) if sx < width - 1 else False) | ((grid_rd.horizontal[sy, sx-1] & (moves[i] == 1)) if sx > 0 else False) | ((grid_lu.vertical[sy, sx] & (moves[i] == 2)) if sy < height - 1 else False) | ((grid_rd.vertical[sy-1, sx] & (moves[i] == 3)) if sy > 0 else False)))
            solver.ensure(fold_or(conditions))

    is_sat = solver.solve()
    return is_sat, grid, order_array

def _main3():
    height = 14
    width = 14
    walls_h = [(4, 9), (7, 4), (8, 0), (9, 0), (9, 1), (10, 9), (11, 5), (11, 9), (11, 11), (13, 2)]
    walls_v = [(1, 6), (2, 6), (3, 6), (6, 1), (6, 2), (7, 1), (8, 2), (8, 6), (9, 10), (11, 7), (11, 12), (12, 1), (12, 4), (12, 5), (12, 6), (12, 8)]
    blacks = [(0, 0), (0, 5), (5, 8), (5, 10), (6, 5), (9, 4), (11, 2), (12, 8), (13, 13)]
    reds = [(2, 4), (5, 7), (9, 12)]
    whites = [(1, 9), (3, 2), (3, 9), (5, 1)]
    letters = {"B": [(0, 1), (1, 5), (5, 9), (5, 11), (6, 1), (6, 4), (6, 6), (8, 4), (9, 5), (11, 8), (12, 2), (12, 7), (12, 9), (13, 12)], "L": [(1, 1), (1, 6), (2, 5), (3, 13), (5, 12), (6, 9), (6, 10), (7, 4), (9, 6), (10, 8), (12, 10), (13, 2), (13, 11)], "A": [(0, 6), (1, 2), (1, 4), (5, 13), (7, 3), (7, 9), (8, 2), (9, 7), (9, 8), (10, 6), (13, 1), (13, 10)], "C": [(0, 2), (0, 7), (0, 12), (3, 5), (4, 10), (6, 3), (6, 13), (8, 8), (8, 9), (10, 7), (11, 6), (13, 0), (13, 5), (13, 9)], "K": [(0, 3), (0, 8), (6, 2), (6, 12), (8, 7), (9, 3), (9, 9), (11, 7), (12, 0), (13, 8)], "R": [(0, 4), (2, 3), (4, 9), (6, 7), (8, 1), (8, 12), (9, 2), (9, 13), (10, 11), (12, 5)], "E": [(1, 12), (2, 2), (2, 11), (3, 7), (4, 2), (4, 8), (5, 6), (6, 8), (7, 7), (8, 11), (10, 13), (11, 13)], "D": [(2, 1), (2, 6), (4, 6), (4, 7), (7, 0), (7, 5), (7, 8), (7, 11), (11, 4), (12, 13)], "W": [(1, 10), (3, 1), (3, 10), (5, 2), (7, 1), (11, 5)], "H": [(0, 10), (3, 0), (3, 11), (5, 3)], "I": [(0, 11), (3, 12), (4, 0), (5, 4)], "T": [(1, 11), (2, 12), (4, 1), (5, 5), (10, 1)]}
    start = (3, 8)
    end = (12, 12)
    is_sat, grid, order_array = solve_maze3(height, width, walls_h, walls_v, blacks, reds, whites, letters, start, end)
    print("maze 3:", is_sat)
    if is_sat:
        print("grid:")
        print(puz_util.stringify_grid_frame(grid))
        print("order_array:")
        print(puz_util.stringify_array(order_array, lambda x: "XXX" if x == -1 else "???" if x == None else str(x).zfill(3)))


def solve_maze4(height, width, blocks, walls_h, walls_v, numbers, arrows, keys, locks, start, end):
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

    for y, x in arrows["l"]:
        solver.ensure(grid_lu.horizontal[y, x] & grid_lu.horizontal[y, x-1])
    for y, x in arrows["r"]:
        solver.ensure(grid_rd.horizontal[y, x] & grid_rd.horizontal[y, x-1])
    for y, x in arrows["u"]:
        solver.ensure(grid_lu.vertical[y, x] & grid_lu.vertical[y-1, x])
    for y, x in arrows["d"]:
        solver.ensure(grid_rd.vertical[y, x] & grid_rd.vertical[y-1, x])
    for y, x in arrows["h"]:
        solver.ensure((grid_lu.horizontal[y, x] & grid_lu.horizontal[y, x-1]) | (grid_rd.horizontal[y, x] & grid_rd.horizontal[y, x-1]))
    for y, x in arrows["v"]:
        solver.ensure((grid_lu.vertical[y, x] & grid_lu.vertical[y-1, x]) | (grid_rd.vertical[y, x] & grid_rd.vertical[y-1, x]))

    index_array = solver.int_array((len(keys) + len(locks), 1), 0, height * width - 1)
    solver.add_answer_key(index_array)
    for i in range(len(keys) + len(locks) - 1):
        solver.ensure(index_array[i] < index_array[i+1])

    for y, x in keys:
        solver.ensure(is_passed[y, x])
        solver.ensure(fold_or([index_array[2*i, 0] == order_array[y, x] for i in range(len(keys))]))
    for y, x in locks:
        solver.ensure(is_passed[y, x])
        solver.ensure(fold_or([index_array[2*i+1, 0] == order_array[y, x] for i in range(len(locks))]))

    is_sat = solver.solve()
    return is_sat, grid, order_array

def _main4():
    height = 14
    width = 14
    blocks = [(2, 3), (3, 10), (5, 2), (7, 7), (8, 2), (8, 4), (10, 2), (10, 4), (12, 2), (12, 4), (4, 10), (9, 12), (10, 3), (10, 12), (12, 0)]
    walls_h = [(4, 3), (10, 0), (12, 0)]
    walls_v = [(4, 4), (7, 0)]
    numbers = [(7, 12, 8), (8, 1, 6), (8, 3, 6), (8, 12, 7), (12, 3, 6)]
    arrows = {"l": [(2, 1), (6, 6), (7, 2)], "r": [(0, 7), (4, 2), (5, 8), (6, 1), (9, 4)], "u": [(1, 4), (1, 6), (4, 11), (8, 8), (9, 9), (9, 11)], "d": [(9, 7), (10, 6)], "h": [(0, 1), (1, 1), (8, 6), (11, 4), (12, 6), (12, 8), (13, 6)], "v": [(6, 11), (7, 5), (12, 12)]}
    keys = [(6, 10), (8, 9), (9, 0), (12, 11)]
    locks = [(6, 9), (9, 2), (10, 11), (13, 11)]
    start = (3, 9)
    end = (11, 12)
    is_sat, grid, order_array = solve_maze4(height, width, blocks, walls_h, walls_v, numbers, arrows, keys, locks, start, end)
    print("maze 4:", is_sat)
    if is_sat:
        print("grid:")
        print(puz_util.stringify_grid_frame(grid))
        print("order_array:")
        print(puz_util.stringify_array(order_array, lambda x: "XXX" if x == -1 else "???" if x == None else str(x).zfill(3)))



def solve_maze5(height, width, blocks, walls_h, walls_v, numbers, reds, whites,letters, arrows, keys, locks, start, end):
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

    grid_rd, grid_lu, order_array = get_direction_order(solver, grid, is_passed, height, width, start, end)
    to_up, to_down, to_left, to_right = get_pathlength(solver, grid, height, width)
    
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

    for y, x in arrows["l"]:
        solver.ensure(grid_lu.horizontal[y, x] & grid_lu.horizontal[y, x-1])
    for y, x in arrows["r"]:
        solver.ensure(grid_rd.horizontal[y, x] & grid_rd.horizontal[y, x-1])
    for y, x in arrows["u"]:
        solver.ensure(grid_lu.vertical[y, x] & grid_lu.vertical[y-1, x])
    for y, x in arrows["d"]:
        solver.ensure(grid_rd.vertical[y, x] & grid_rd.vertical[y-1, x])
    for y, x in arrows["h"]:
        solver.ensure((grid_lu.horizontal[y, x] & grid_lu.horizontal[y, x-1]) | (grid_rd.horizontal[y, x] & grid_rd.horizontal[y, x-1]))
    for y, x in arrows["v"]:
        solver.ensure((grid_lu.vertical[y, x] & grid_lu.vertical[y-1, x]) | (grid_rd.vertical[y, x] & grid_rd.vertical[y-1, x]))

    for y, x in reds:
        name = "RED"
        moves = solver.int_array(len(name), 0, 3)
        curr_y, curr_x = y, x
        for i in range(len(name)):
            curr_y, curr_x = curr_y + ((moves[i] == 0) | (moves[i] == 1)).cond(0, (moves[i] == 2).cond(-1, 1)), curr_x + ((moves[i] == 2) | (moves[i] == 3)).cond(0, (moves[i] == 0).cond(-1, 1))
            conditions = []
            for sy, sx in letters[name[i]]:
                conditions.append((curr_y == sy) & (curr_x == sx) & (((grid_lu.horizontal[sy, sx] & (moves[i] == 0)) if sx < width - 1 else False) | ((grid_rd.horizontal[sy, sx-1] & (moves[i] == 1)) if sx > 0 else False) | ((grid_lu.vertical[sy, sx] & (moves[i] == 2)) if sy < height - 1 else False) | ((grid_rd.vertical[sy-1, sx] & (moves[i] == 3)) if sy > 0 else False)))
            solver.ensure(fold_or(conditions))

    for y, x in whites:
        name = "WHITE"
        moves = solver.int_array(len(name), 0, 3)
        curr_y, curr_x = y, x
        for i in range(len(name)):
            curr_y, curr_x = curr_y + ((moves[i] == 0) | (moves[i] == 1)).cond(0, (moves[i] == 2).cond(-1, 1)), curr_x + ((moves[i] == 2) | (moves[i] == 3)).cond(0, (moves[i] == 0).cond(-1, 1))
            conditions = []
            for sy, sx in letters[name[i]]:
                conditions.append((curr_y == sy) & (curr_x == sx) & (((grid_lu.horizontal[sy, sx] & (moves[i] == 0)) if sx < width - 1 else False) | ((grid_rd.horizontal[sy, sx-1] & (moves[i] == 1)) if sx > 0 else False) | ((grid_lu.vertical[sy, sx] & (moves[i] == 2)) if sy < height - 1 else False) | ((grid_rd.vertical[sy-1, sx] & (moves[i] == 3)) if sy > 0 else False)))
            solver.ensure(fold_or(conditions))
    
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
    
    index_array = solver.int_array((len(keys) + len(locks), 1), 0, height * width - 1)
    solver.add_answer_key(index_array)
    for i in range(len(keys) + len(locks) - 1):
        solver.ensure(index_array[i] < index_array[i+1])
    for y, x in keys:
        solver.ensure(is_passed[y, x])
        solver.ensure(fold_or([index_array[2*i, 0] == order_array[y, x] for i in range(len(keys))]))
    for y, x in locks:
        solver.ensure(is_passed[y, x])
        solver.ensure(fold_or([index_array[2*i+1, 0] == order_array[y, x] for i in range(len(locks))]))
    
    is_sat = solver.solve()
    return is_sat, grid, order_array

def _main5():
    height = 14
    width = 35
    blocks = [(0, 7), (0, 12), (1, 22), (1, 26), (1, 33), (2, 3), (3, 24), (3, 31), (5, 2), (5, 22), (5, 26), (5, 29), (6, 12), (7, 21), (7, 29), (8, 2), (8, 4), (8, 32), (9, 11), (9, 21), (9, 33), (10, 2), (10, 4), (11, 9), (11, 31), (11, 34), (12, 2), (12, 4), (13, 24), (0, 14), (0, 27), (1, 34), (7, 20), (9, 25), (10, 3), (10, 12), (12, 0)]
    walls_h = [(0, 23), (3, 28), (4, 3), (4, 16), (4, 24), (4, 33), (5, 27), (6, 27), (6, 28), (6, 33), (7, 11), (7, 14), (7, 15), (7, 16), (8, 7), (8, 15), (9, 7), (9, 8), (10, 0), (10, 17), (11, 12), (11, 19), (12, 0), (12, 17), (13, 9)]
    walls_v = [(0, 17), (0, 24), (1, 13), (1, 28), (2, 13), (2, 14), (2, 15), (2, 25), (2, 27), (2, 34), (3, 13), (3, 28), (4, 4), (4, 14), (4, 15), (5, 19), (5, 21), (6, 8), (6, 9), (6, 23), (7, 0), (7, 8), (7, 15), (8, 9), (8, 13), (8, 15), (10, 18), (11, 14), (11, 15), (11, 17), (11, 19), (12, 8), (12, 11), (12, 12), (12, 13), (12, 14)]
    numbers = [(1, 15, 5), (1, 19, 8), (1, 24, 6), (1, 28, 7), (1, 31, 0), (2, 33, 3), (3, 16, 8), (3, 19, 8), (3, 22, 1), (3, 26, 4), (3, 33, 5), (5, 31, 1), (5, 33, 6), (7, 28, 3), (8, 1, 6), (8, 3, 6), (8, 24, 2), (8, 26, 0), (8, 31, 7), (8, 33, 6), (9, 8, 3), (9, 18, 8), (9, 22, 2), (9, 24, 0), (9, 27, 2), (10, 11, 6), (10, 22, 2), (11, 8, 5), (11, 17, 4), (11, 19, 7), (11, 26, 2), (11, 27, 2), (11, 28, 2), (12, 3, 6), (12, 15, 3), (12, 22, 6), (13, 29, 0), (13, 34, 1)]
    reds = [(2, 11), (2, 16), (2, 18), (4, 16), (4, 18), (10, 17)]
    whites = [(3, 9), (5, 8)]
    letters = {"R": [(0, 2), (0, 11), (1, 16), (1, 18), (2, 2), (2, 10), (2, 15), (2, 19), (2, 25), (4, 15), (4, 33), (5, 16), (5, 18), (8, 8), (8, 15), (8, 23), (8, 27), (9, 9), (9, 17), (11, 6), (11, 33), (12, 5), (12, 12), (13, 3), (13, 15), (13, 33)], "E": [(0, 18), (2, 9), (2, 14), (2, 20), (2, 34), (3, 4), (3, 34), (4, 8), (4, 14), (5, 13), (6, 16), (6, 18), (6, 20), (6, 26), (6, 28), (6, 34), (7, 3), (7, 34), (8, 16), (8, 17), (10, 0), (11, 25)], "D": [(0, 23), (2, 8), (2, 13), (2, 21), (4, 13), (6, 19), (7, 4), (7, 7), (7, 12), (7, 16), (7, 17), (7, 18), (7, 31), (8, 0), (11, 0), (11, 5), (11, 11), (11, 29), (13, 5)], "W": [(3, 8), (5, 9), (6, 14), (7, 8), (10, 20), (13, 21), (13, 22)], "H": [(3, 7), (3, 32), (4, 17), (5, 10), (6, 5), (8, 20), (9, 2), (9, 32), (11, 3), (12, 21), (13, 14), (13, 26)], "I": [(2, 0), (2, 29), (3, 6), (3, 25), (4, 7), (4, 22), (5, 11), (5, 24), (6, 30), (6, 33), (7, 30), (9, 5), (10, 28), (12, 25)], "T": [(0, 31), (2, 7), (2, 27), (3, 3), (3, 5), (4, 3), (4, 8), (4, 27), (5, 1), (5, 12), (5, 25), (10, 8), (10, 32), (12, 17), (12, 19), (13, 20)]}
    arrows = {"l": [(2, 1), (6, 6), (7, 2)], "r": [(4, 2), (6, 1), (9, 4), (13, 13)], "u": [(1, 4), (1, 6)], "d": [(10, 6)], "h": [(0, 1), (1, 1), (8, 6), (11, 4), (12, 6), (13, 6)], "v": [(7, 5)]}
    keys = [(9, 0)]
    locks = [(9, 2)]
    start = (0, 26)
    end = (6, 24)
    is_sat, grid, order_array = solve_maze5(height, width, blocks, walls_h, walls_v, numbers, reds, whites, letters, arrows, keys, locks, start, end)
    print("maze 5:", is_sat)
    if is_sat:
        print("grid:")
        print(puz_util.stringify_grid_frame(grid))
        print("order_array:")
        print(puz_util.stringify_array(order_array, lambda x: "XXX" if x == -1 else "???" if x == None else str(x).zfill(3)))


if __name__ == "__main__":
    _main5()