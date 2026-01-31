from cspuz import graph, Solver, count_true, BoolGridFrame
from cspuz.puzzle import util as puz_util
from util import get_direction_order, get_pathlength
from cspuz.array import BoolArray1D, IntArray1D
from typing import Tuple
from cspuz.constraints import count_true, fold_or

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


class DiceGrid:
    def __init__(self, solver, depth, height, width):
        self.depth = depth
        self.height = height
        self.width = width
        
        # Surfaces (vertices/cells)
        self.dims = [
        (height, width),  # 0
        (height, depth),  # 1
        (height, width),  # 2
        (depth, width),   # 3
        (depth, height),  # 4
        (depth, width)    # 5
        ]
        
        # Mapping (surface_index, y, x) to vertex index
        self.offsets = [0]
        for s in self.dims:
            self.offsets.append(self.offsets[-1] + s[0] * s[1])
        
        num_vertices = self.offsets[-1]
        self.graph = graph.Graph(num_vertices)
        
        def get_v(s_idx, y, x):
            return self.offsets[s_idx] + y * self.dims[s_idx][1] + x

        self.get_v = get_v

        def from_v(v):
            for s_idx in range(6):
                if self.offsets[s_idx] <= v < self.offsets[s_idx + 1]:
                    local_v = v - self.offsets[s_idx]
                    width = self.dims[s_idx][1]
                    return s_idx, local_v // width, local_v % width
            return None

        self.from_v = from_v

        # Internal connectivity
        for s_idx in range(6):
            h, w = self.dims[s_idx]
            for y in range(h):
                for x in range(w - 1):
                    self.graph.add_edge(get_v(s_idx, y, x), get_v(s_idx, y, x + 1))
            for y in range(h - 1):
                for x in range(w):
                    self.graph.add_edge(get_v(s_idx, y, x), get_v(s_idx, y + 1, x))

        # Cross-surface connectivity
        # Surface 0
        for i in range(height):
            self.graph.add_edge(get_v(0, i, 0), get_v(4, 0, i))
            self.graph.add_edge(get_v(0, i, width - 1), get_v(1, i, 0))
        for i in range(width):
            self.graph.add_edge(get_v(0, 0, i), get_v(3, 0, width - 1 - i))
            self.graph.add_edge(get_v(0, height - 1, i), get_v(5, 0, i))

        # Surface 1
        for i in range(height):
            self.graph.add_edge(get_v(1, i, depth - 1), get_v(2, i, 0))
        for i in range(depth):
            self.graph.add_edge(get_v(1, 0, i), get_v(3, i, 0))
            self.graph.add_edge(get_v(1, height - 1, i), get_v(5, i, width - 1))

        # Surface 2
        for i in range(height):
            self.graph.add_edge(get_v(2, i, width - 1), get_v(4, depth - 1, i))
        for i in range(width):
            self.graph.add_edge(get_v(2, 0, i), get_v(3, depth - 1, i))
            self.graph.add_edge(get_v(2, height - 1, i), get_v(5, depth - 1, width - 1 - i))

        # Surface 3
        for i in range(depth):
            self.graph.add_edge(get_v(3, i, width - 1), get_v(4, i, 0))

        # Surface 4
        for i in range(depth):
            self.graph.add_edge(get_v(4, i, height - 1), get_v(5, i, 0))

def get_adjacent_dice(depth, height, width, s, y, x):
    # Returns (s, y, x) for left, right, up, down
    # Surface dimensions
    dims = [
        (height, width),  # 0
        (height, depth),  # 1
        (height, width),  # 2
        (depth, width),   # 3
        (depth, height),  # 4
        (depth, width)    # 5
    ]
    
    h, w = dims[s]
    
    # Default internal neighbors
    res = [
        (s, y, x - 1) if x > 0 else None, # left
        (s, y, x + 1) if x < w - 1 else None, # right
        (s, y - 1, x) if y > 0 else None, # up
        (s, y + 1, x) if y < h - 1 else None  # down
    ]
    
    # Boundary cases
    if s == 0:
        if x == 0: res[0] = (4, 0, y) # left -> 4 up
        if x == width - 1: res[1] = (1, y, 0) # right -> 1 left
        if y == 0: res[2] = (3, 0, width - 1 - x) # up -> 3 up (flipped)
        if y == height - 1: res[3] = (5, 0, x) # down -> 5 up
    elif s == 1:
        if x == 0: res[0] = (0, y, width - 1) # left -> 0 right
        if x == depth - 1: res[1] = (2, y, 0) # right -> 2 left
        if y == 0: res[2] = (3, x, 0) # up -> 3 left
        if y == height - 1: res[3] = (5, x, width - 1) # down -> 5 right
    elif s == 2:
        if x == 0: res[0] = (1, y, depth - 1) # left -> 1 right
        if x == width - 1: res[1] = (4, depth - 1, y) # right -> 4 down
        if y == 0: res[2] = (3, depth - 1, x) # up -> 3 down
        if y == height - 1: res[3] = (5, depth - 1, width - 1 - x) # down -> 5 down (flipped)
    elif s == 3:
        if x == 0: res[0] = (1, 0, y) # left -> 1 up
        if x == width - 1: res[1] = (4, y, 0) # right -> 4 left
        if y == 0: res[2] = (0, 0, width - 1 - x) # up -> 0 up (flipped)
        if y == depth - 1: res[3] = (2, 0, x) # down -> 2 up
    elif s == 4:
        if x == 0: res[0] = (3, y, width - 1) # left -> 3 right
        if x == height - 1: res[1] = (5, y, 0) # right -> 5 left
        if y == 0: res[2] = (0, x, 0) # up -> 0 left
        if y == depth - 1: res[3] = (2, x, width - 1) # down -> 2 right
    elif s == 5:
        if x == 0: res[0] = (4, y, height - 1) # left -> 4 right
        if x == width - 1: res[1] = (1, height - 1, y) # right -> 1 down
        if y == 0: res[2] = (0, height - 1, x) # up -> 0 down
        if y == depth - 1: res[3] = (2, height - 1, width - 1 - x) # down -> 2 down (flipped)
        
    return res

def active_edges_single_path_dice(solver: Solver, dice_grid: DiceGrid):
    active_edges = solver.bool_array(len(dice_grid.graph.edges))
    is_passed_flat = graph.active_edges_single_path(solver, active_edges, dice_grid.graph)
    return active_edges, is_passed_flat

def get_edge_var(dice_grid, active_edges, u, v):
    for neighbor, edge_id in dice_grid.graph.incident_edges[u]:
        if neighbor == v:
            return active_edges[edge_id]
    return None

def get_v(dice_grid, s_idx, y, x):
    return dice_grid.offsets[s_idx] + y * dice_grid.dims[s_idx][1] + x

def get_pathlength_dice(solver: Solver, dice_grid: DiceGrid, active_edges):
    dims = dice_grid.dims
    num_dims = 6
    max_len = dice_grid.width + dice_grid.height + dice_grid.depth
    
    to_up = [solver.int_array(dim, 0, max_len) for dim in dims]
    to_down = [solver.int_array(dim, 0, max_len) for dim in dims]
    to_left = [solver.int_array(dim, 0, max_len) for dim in dims]
    to_right = [solver.int_array(dim, 0, max_len) for dim in dims]

    for s_idx in range(num_dims):
        h, w = dims[s_idx]
        for y in range(h):
            for x in range(w):
                # Internal propagation
                # to_up[y, x] depends on the vertical edge above it
                if y > 0:
                    edge = get_edge_var(dice_grid, active_edges, get_v(dice_grid, s_idx, y, x), get_v(dice_grid, s_idx, y - 1, x))
                    solver.ensure(to_up[s_idx][y, x] == (edge.cond(to_up[s_idx][y-1, x] + 1, 0)))
                # to_down[y, x] depends on the vertical edge below it
                if y < h - 1:
                    edge = get_edge_var(dice_grid, active_edges, get_v(dice_grid, s_idx, y, x), get_v(dice_grid, s_idx, y + 1, x))
                    solver.ensure(to_down[s_idx][y, x] == (edge.cond(to_down[s_idx][y+1, x] + 1, 0)))
                # to_left[y, x] depends on the horizontal edge to its left
                if x > 0:
                    edge = get_edge_var(dice_grid, active_edges, get_v(dice_grid, s_idx, y, x), get_v(dice_grid, s_idx, y, x - 1))
                    solver.ensure(to_left[s_idx][y, x] == (edge.cond(to_left[s_idx][y, x-1] + 1, 0)))
                # to_right[y, x] depends on the horizontal edge to its right
                if x < w - 1:
                    edge = get_edge_var(dice_grid, active_edges, get_v(dice_grid, s_idx, y, x), get_v(dice_grid, s_idx, y, x + 1))
                    solver.ensure(to_right[s_idx][y, x] == (edge.cond(to_right[s_idx][y, x+1] + 1, 0)))

    # Boundary propagation: when a path crosses a boundary, the count continues
    # in the direction perpendicular to the boundary.
    
    # Surface 0
    for i in range(dice_grid.height):
        # Left (x=0) boundary connects to Surface 4 Up (y=0)
        edge_0_4 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 0, i, 0), get_v(dice_grid, 4, 0, i))
        solver.ensure(to_left[0][i, 0] == edge_0_4.cond(to_down[4][0, i] + 1, 0))
        solver.ensure(to_up[4][0, i] == edge_0_4.cond(to_right[0][i, 0] + 1, 0))
        
        # Right (x=width-1) boundary connects to Surface 1 Left (x=0)
        edge_0_1 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 0, i, dice_grid.width - 1), get_v(dice_grid, 1, i, 0))
        solver.ensure(to_right[0][i, dice_grid.width-1] == edge_0_1.cond(to_right[1][i, 0] + 1, 0))
        solver.ensure(to_left[1][i, 0] == edge_0_1.cond(to_left[0][i, dice_grid.width-1] + 1, 0))
        
    for i in range(dice_grid.width):
        # Up (y=0) boundary connects to Surface 3 Up (y=0) (flipped)
        edge_0_3 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 0, 0, i), get_v(dice_grid, 3, 0, dice_grid.width - 1 - i))
        solver.ensure(to_up[0][0, i] == edge_0_3.cond(to_down[3][0, dice_grid.width-1-i] + 1, 0))
        solver.ensure(to_up[3][0, dice_grid.width-1-i] == edge_0_3.cond(to_down[0][0, i] + 1, 0))
        
        # Down (y=height-1) boundary connects to Surface 5 Up (y=0)
        edge_0_5 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 0, dice_grid.height - 1, i), get_v(dice_grid, 5, 0, i))
        solver.ensure(to_down[0][dice_grid.height-1, i] == edge_0_5.cond(to_down[5][0, i] + 1, 0))
        solver.ensure(to_up[5][0, i] == edge_0_5.cond(to_up[0][dice_grid.height-1, i] + 1, 0))

    # Surface 1
    for i in range(dice_grid.height):
        # Right (x=depth-1) boundary connects to Surface 2 Left (x=0)
        edge_1_2 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 1, i, dice_grid.depth - 1), get_v(dice_grid, 2, i, 0))
        solver.ensure(to_right[1][i, dice_grid.depth-1] == edge_1_2.cond(to_right[2][i, 0] + 1, 0))
        solver.ensure(to_left[2][i, 0] == edge_1_2.cond(to_left[1][i, dice_grid.depth-1] + 1, 0))
        
    for i in range(dice_grid.depth):
        # Up (y=0) boundary connects to Surface 3 Left (x=0)
        edge_1_3 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 1, 0, i), get_v(dice_grid, 3, i, 0))
        solver.ensure(to_up[1][0, i] == edge_1_3.cond(to_right[3][i, 0] + 1, 0))
        solver.ensure(to_left[3][i, 0] == edge_1_3.cond(to_down[1][0, i] + 1, 0))
        
        # Down (y=height-1) boundary connects to Surface 5 Right (x=width-1)
        edge_1_5 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 1, dice_grid.height - 1, i), get_v(dice_grid, 5, i, dice_grid.width - 1))
        solver.ensure(to_down[1][dice_grid.height-1, i] == edge_1_5.cond(to_left[5][i, dice_grid.width-1] + 1, 0))
        solver.ensure(to_right[5][i, dice_grid.width-1] == edge_1_5.cond(to_up[1][dice_grid.height-1, i] + 1, 0))

    # Surface 2
    for i in range(dice_grid.height):
        # Right (x=width-1) boundary connects to Surface 4 Down (y=depth-1)
        edge_2_4 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 2, i, dice_grid.width - 1), get_v(dice_grid, 4, dice_grid.depth - 1, i))
        solver.ensure(to_right[2][i, dice_grid.width-1] == edge_2_4.cond(to_up[4][dice_grid.depth-1, i] + 1, 0))
        solver.ensure(to_down[4][dice_grid.depth-1, i] == edge_2_4.cond(to_left[2][i, dice_grid.width-1] + 1, 0))
        
    for i in range(dice_grid.width):
        # Up (y=0) boundary connects to Surface 3 Down (y=depth-1)
        edge_2_3 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 2, 0, i), get_v(dice_grid, 3, dice_grid.depth - 1, i))
        solver.ensure(to_up[2][0, i] == edge_2_3.cond(to_up[3][dice_grid.depth-1, i] + 1, 0))
        solver.ensure(to_down[3][dice_grid.depth-1, i] == edge_2_3.cond(to_down[2][0, i] + 1, 0))
        
        # Down (y=height-1) boundary connects to Surface 5 Down (y=depth-1) (flipped)
        edge_2_5 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 2, dice_grid.height - 1, i), get_v(dice_grid, 5, dice_grid.depth - 1, dice_grid.width - 1 - i))
        solver.ensure(to_down[2][dice_grid.height-1, i] == edge_2_5.cond(to_up[5][dice_grid.depth-1, dice_grid.width-1-i] + 1, 0))
        solver.ensure(to_down[5][dice_grid.depth-1, dice_grid.width-1-i] == edge_2_5.cond(to_up[2][dice_grid.height-1, i] + 1, 0))

    # Surface 3
    for i in range(dice_grid.depth):
        # Right (x=width-1) boundary connects to Surface 4 Left (x=0)
        edge_3_4 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 3, i, dice_grid.width - 1), get_v(dice_grid, 4, i, 0))
        solver.ensure(to_right[3][i, dice_grid.width-1] == edge_3_4.cond(to_right[4][i, 0] + 1, 0))
        solver.ensure(to_left[4][i, 0] == edge_3_4.cond(to_left[3][i, dice_grid.width-1] + 1, 0))

    # Surface 4
    for i in range(dice_grid.depth):
        # Right (x=height-1) boundary connects to Surface 5 Left (x=0)
        edge_4_5 = get_edge_var(dice_grid, active_edges, get_v(dice_grid, 4, i, dice_grid.height - 1), get_v(dice_grid, 5, i, 0))
        solver.ensure(to_right[4][i, dice_grid.height-1] == edge_4_5.cond(to_right[5][i, 0] + 1, 0))
        solver.ensure(to_left[5][i, 0] == edge_4_5.cond(to_left[4][i, dice_grid.height-1] + 1, 0))

    return to_up, to_down, to_left, to_right

def get_neighbor_order(dice_grid: DiceGrid, grid_g: BoolArray1D, grid_l: BoolArray1D, order_array: IntArray1D, s: int, y: int, x: int) -> BoolArray1D:
    neighbor_edges = dice_grid.graph.incident_edges[get_v(dice_grid, s, y, x)]
    neighbor_order = []
    own = get_v(dice_grid, s, y, x)
    for neighbor, edge_id in neighbor_edges:
        neighbor_s, neighbor_y, neighbor_x = dice_grid.from_v(neighbor)
        if neighbor > own:
            neighbor_order.append(grid_g[edge_id] & (order_array[neighbor_s][neighbor_y, neighbor_x] == order_array[s][y, x] + 1))
        else:
            neighbor_order.append(grid_l[edge_id] & (order_array[neighbor_s][neighbor_y, neighbor_x] == order_array[s][y, x] + 1))
    return BoolArray1D(neighbor_order)

def get_direction_order_dice(solver: Solver, dice_grid: DiceGrid, active_edges: BoolArray1D, is_passed_flat: BoolArray1D, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> Tuple[BoolArray1D, BoolArray1D, IntArray1D]:
    grid_g = solver.bool_array(len(dice_grid.graph.edges))
    grid_l = solver.bool_array(len(dice_grid.graph.edges))
    solver.add_answer_key(grid_g)
    solver.add_answer_key(grid_l)
    solver.ensure(((~active_edges) & (~grid_g) & (~grid_l)) | ((active_edges) & (grid_g) & (~grid_l)) | ((active_edges) & (~grid_g) & (grid_l)))

    n_max = 2*dice_grid.width*dice_grid.height + 2*dice_grid.depth*dice_grid.width + 2*dice_grid.height*dice_grid.depth
    order_array = [solver.int_array((dice_grid.dims[s][0], dice_grid.dims[s][1]), -1, n_max) for s in range(6)]
    solver.add_answer_key(order_array)

    for s in range(6):
        for y in range(order_array[s].shape[0]):
            for x in range(order_array[s].shape[1]):
                if (s, y, x) != start and (s, y, x) != end:
                    solver.ensure((is_passed_flat[get_v(dice_grid, s, y, x)]).then(order_array[s][y, x] > 0))
                    solver.ensure((~is_passed_flat[get_v(dice_grid, s, y, x)]).then(order_array[s][y, x] == -1))
                    solver.ensure((is_passed_flat[get_v(dice_grid, s, y, x)]).then(count_true(get_neighbor_order(dice_grid, grid_g, grid_l, order_array, s, y, x)) == 1))
                elif (s, y, x) == start:
                    solver.ensure(order_array[s][y, x] == 0)
                    solver.ensure(count_true(get_neighbor_order(dice_grid, grid_g, grid_l, order_array, s, y, x)) == 1)

    return grid_g, grid_l, order_array

def solve_dice(height, width, depth, blocks, walls_h, walls_v, numbers, walls_edge, reds, letters, arrows, keys, locks, start, end):
    solver = Solver()
    dice_grid = DiceGrid(solver, height, width, depth)

    active_edges, is_passed_flat = active_edges_single_path_dice(solver, dice_grid)
    grid_g, grid_l, order_array = get_direction_order_dice(solver, dice_grid, active_edges, is_passed_flat, start, end)
    to_up, to_down, to_left, to_right = get_pathlength_dice(solver, dice_grid, active_edges)
    solver.add_answer_key(active_edges)
    solver.add_answer_key(is_passed_flat)

    for s, y, x in blocks:
        solver.ensure(~is_passed_flat[get_v(dice_grid, s, y, x)])
    
    for s, y, x in walls_h:
        solver.ensure(~get_edge_var(dice_grid, active_edges, get_v(dice_grid, s, y, x), get_v(dice_grid, s, y, x + 1)))
    for s, y, x in walls_v:
        solver.ensure(~get_edge_var(dice_grid, active_edges, get_v(dice_grid, s, y, x), get_v(dice_grid, s, y + 1, x)))
    for u, v in walls_edge:
        solver.ensure(~get_edge_var(dice_grid, active_edges, get_v(dice_grid, *u), get_v(dice_grid, *v)))

    for s, y, x, n in numbers:
        left, right, up, down = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, s, y, x)
        left_left, left_right, left_up, left_down = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, *left)
        right_left, right_right, right_up, right_down = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, *right)
        neighbors = [left, right, up, down, left_up, left_down, right_up, right_down]
        solver.ensure(count_true([is_passed_flat[get_v(dice_grid, *i)] for i in neighbors]) == n)

    for s, y, x in reds:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        left, right, up, down = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, s, y, x)
        left_in = get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *left)) if (get_v(dice_grid, *left) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *left))
        right_in = get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *right)) if (get_v(dice_grid, *right) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *right))
        up_in = get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *up)) if (get_v(dice_grid, *up) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *up))
        down_in = get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *down)) if (get_v(dice_grid, *down) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *down))
        left_out = get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *left)) if (get_v(dice_grid, *left) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *left))
        right_out = get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *right)) if (get_v(dice_grid, *right) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *right))
        up_out = get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *up)) if (get_v(dice_grid, *up) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *up))
        down_out = get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *down)) if (get_v(dice_grid, *down) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *down))
        conditions = []
        conditions.append(left_in & up_out & (to_left[s][y, x] == to_up[s][y, x] + 2))
        conditions.append(left_in & down_out & (to_left[s][y, x] == to_down[s][y, x] + 2))
        conditions.append(right_in & up_out & (to_right[s][y, x] == to_up[s][y, x] + 2))
        conditions.append(right_in & down_out & (to_right[s][y, x] == to_down[s][y, x] + 2))
        conditions.append(up_in & left_out & (to_up[s][y, x] == to_left[s][y, x] + 2))
        conditions.append(up_in & right_out & (to_up[s][y, x] == to_right[s][y, x] + 2))
        conditions.append(down_in & left_out & (to_down[s][y, x] == to_left[s][y, x] + 2))
        conditions.append(down_in & right_out & (to_down[s][y, x] == to_right[s][y, x] + 2))
        solver.ensure(fold_or(conditions))

    for s, y, x in reds:
        words = []
        for i in range(4):
            one_word = []
            curr_s, curr_y, curr_x = s, y, x
            for t in range(3):
                curr_s, curr_y, curr_x = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, curr_s, curr_y, curr_x)[i]
                one_word.append((curr_s, curr_y, curr_x))
            words.append(one_word)
        step_1 = [get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *words[i][0])) if (get_v(dice_grid, *words[i][0]) > get_v(dice_grid, s, y, x)) else get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *words[i][0])) for i in range(len(words))]
        step_2 = [get_edge_var(dice_grid, grid_g, get_v(dice_grid, *words[i][0]), get_v(dice_grid, *words[i][1])) if (get_v(dice_grid, *words[i][1]) > get_v(dice_grid, *words[i][0])) else get_edge_var(dice_grid, grid_l, get_v(dice_grid, *words[i][0]), get_v(dice_grid, *words[i][1])) for i in range(len(words))]
        step_3 = [get_edge_var(dice_grid, grid_g, get_v(dice_grid, *words[i][1]), get_v(dice_grid, *words[i][2])) if (get_v(dice_grid, *words[i][2]) > get_v(dice_grid, *words[i][1])) else get_edge_var(dice_grid, grid_l, get_v(dice_grid, *words[i][1]), get_v(dice_grid, *words[i][2])) for i in range(len(words))]
        solver.ensure(fold_or([fold_or([words[i][0] == k for k in letters["R"]]) & fold_or([words[i][1] == k for k in letters["E"]]) & fold_or([words[i][2] == k for k in letters["D"]]) & (step_1[i]) & (step_2[i]) & (step_3[i]) for i in range(len(words))]))


    index_array = solver.int_array((len(keys) + len(locks), 1), 0, 2 * height * width + 2 * height * depth + 2 * width * depth - 1)
    solver.add_answer_key(index_array)
    for i in range(len(keys) + len(locks) - 1):
        solver.ensure(index_array[i] < index_array[i+1])

    for s, y, x in keys:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        solver.ensure(fold_or([index_array[2*i, 0] == order_array[s][y, x] for i in range(len(keys))]))
    for s, y, x in locks:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        solver.ensure(fold_or([index_array[2*i+1, 0] == order_array[s][y, x] for i in range(len(locks))]))

    start_edges = dice_grid.graph.incident_edges[get_v(dice_grid, start[0], start[1], start[2])]
    start_count = []
    for neighbor, edge_id in start_edges:
        start_count.append(active_edges[edge_id])
    solver.ensure(count_true(start_count) == 1)
    end_edges = dice_grid.graph.incident_edges[get_v(dice_grid, end[0], end[1], end[2])]
    end_count = []
    for neighbor, edge_id in end_edges:
        end_count.append(active_edges[edge_id])
    solver.ensure(count_true(end_count) == 1)
    
    for s, y, x in blocks:
        solver.ensure(~is_passed_flat[get_v(dice_grid, s, y, x)])

    for s, y, x in arrows["r"]:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        left, right, up, down = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, s, y, x)
        if get_v(dice_grid, *right) > get_v(dice_grid, s, y, x):
            solver.ensure(get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *right)))
        else:
            solver.ensure(get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *right)))
        if get_v(dice_grid, *left) < get_v(dice_grid, s, y, x):
            solver.ensure(get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *left)))
        else:
            solver.ensure(get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *left)))
    for s, y, x in arrows["l"]:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        left, right, up, down = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, s, y, x)
        if get_v(dice_grid, *left) > get_v(dice_grid, s, y, x):
            solver.ensure(get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *left)))
        else:
            solver.ensure(get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *left)))
        if get_v(dice_grid, *right) < get_v(dice_grid, s, y, x):
            solver.ensure(get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *right)))
        else:
            solver.ensure(get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *right)))
    for s, y, x in arrows["u"]:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        left, right, up, down = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, s, y, x)
        if get_v(dice_grid, *up) > get_v(dice_grid, s, y, x):
            solver.ensure(get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *up)))
        else:
            solver.ensure(get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *up)))
        if get_v(dice_grid, *down) < get_v(dice_grid, s, y, x):
            solver.ensure(get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *down)))
        else:
            solver.ensure(get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *down)))
    for s, y, x in arrows["d"]:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        left, right, up, down = get_adjacent_dice(dice_grid.height, dice_grid.width, dice_grid.depth, s, y, x)
        if get_v(dice_grid, *down) > get_v(dice_grid, s, y, x):
            solver.ensure(get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *down)))
        else:
            solver.ensure(get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *down)))
        if get_v(dice_grid, *up) < get_v(dice_grid, s, y, x):
            solver.ensure(get_edge_var(dice_grid, grid_g, get_v(dice_grid, s, y, x), get_v(dice_grid, *up)))
        else:
            solver.ensure(get_edge_var(dice_grid, grid_l, get_v(dice_grid, s, y, x), get_v(dice_grid, *up)))
    for s, y, x in arrows["h"]:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        solver.ensure(to_left[s][y, x] > 0)
        solver.ensure(to_right[s][y, x] > 0)
    for s, y, x in arrows["v"]:
        solver.ensure(is_passed_flat[get_v(dice_grid, s, y, x)])
        solver.ensure(to_up[s][y, x] > 0)
        solver.ensure(to_down[s][y, x] > 0)

    is_sat = solver.solve()
    return is_sat, is_passed_flat, order_array

def _main_dice():
    height = 7
    width = 7
    depth = 7
    start = (4, 0, 5)
    end = (4, 6, 3)
    blocks = [(0, 1, 2), (0, 1, 4), (0, 3, 2), (0, 3, 4), (0, 5, 2), (0, 5, 4), (1, 2, 4), (1, 4, 2), (4, 1, 1), (4, 1, 5), (4, 3, 3), (4, 5, 1), (4, 5, 5), (5, 1, 5), (5, 3, 3), (5, 5, 1), (0, 3, 3), (0, 5, 0), (1, 3, 5), (2, 0, 6), (4, 0, 6), (5, 1, 6)]
    walls_h = [(0, 3, 0), (0, 5, 0), (1, 0, 4), (1, 1, 0), (1, 2, 0), (1, 2, 1), (1, 4, 5), (1, 6, 2), (2, 0, 0), (2, 0, 1), (2, 0, 2), (2, 1, 1), (2, 3, 3), (2, 4, 5), (2, 6, 3), (3, 4, 2), (4, 0, 2), (4, 4, 3), (5, 3, 0), (5, 4, 5), (5, 6, 0), (5, 6, 5)]
    walls_v = [(0, 0, 0), (1, 0, 1), (1, 1, 2), (1, 1, 6), (1, 5, 1), (1, 5, 4), (1, 5, 5), (1, 5, 6), (2, 0, 1), (2, 1, 1), (2, 3, 4), (2, 4, 0), (2, 4, 1), (2, 4, 3), (2, 4, 5), (3, 0, 3), (3, 2, 0), (3, 2, 1), (3, 4, 0), (3, 4, 1), (3,5, 5), (4, 0, 3), (4, 2, 4), (4, 2, 6), (4, 5, 0), (5, 1, 0), (5, 2, 6), (5, 3, 0)]
    walls_edge = [((1, 0, 1), (3, 1, 0)), ((1, 0, 2), (3, 2, 0)), ((4, 5, 6), (5, 5, 0)), ((4, 6, 6), (5, 6, 0))]
    numbers = [(0, 1, 1, 6), (0, 1, 3, 6), (0, 5, 3, 6), (1, 2, 1, 3), (1, 3, 4, 6), (1, 4, 1, 5), (2, 2, 4, 8), (2, 4, 3, 4), (2, 4, 5, 7), (2, 5, 1, 3), (3, 1, 1, 5), (3, 1, 5, 8), (3, 3, 2, 8), (3, 3, 5, 8), (4, 1, 3, 6), (4, 3, 1, 1), (4, 3, 5, 4), (5, 1, 0, 7), (5, 1, 3, 0), (5, 2, 5, 3), (5, 3, 5, 5), (5, 5, 3, 1), (5, 5, 5, 6)]
    reds = [(2, 3, 3), (3, 2, 2), (3, 2, 4), (3, 4, 2), (3, 4, 4)]
    letters = {"R": [(0, 4, 6), (0, 5, 5), (0, 6, 3), (1, 1, 1), (1, 2, 2), (1, 5, 5), (2, 1, 1), (2, 2, 3), (2, 6, 1), (3, 1, 2), (3, 1, 4), (3, 2, 1), (3, 2, 5), (3, 4, 1), (3, 5, 2), (3, 5, 4), (4, 2, 4), (5, 4, 5)], "E": [(0, 0, 3), (2, 1, 2), (2, 1, 3), (3, 0, 2), (3, 0, 4), (3, 2, 0) ,(3, 2, 6), (3, 4, 0), (3, 6, 2), (3, 6, 4), (3, 6, 6), (4, 6, 5), (5, 2, 6), (5, 3, 6), (5, 6, 1), (5, 6, 6)], "D": [(0, 0, 4), (0, 4, 0), (0, 4, 5), (0, 6, 5), (1, 0, 0), (1, 0, 5), (1, 4, 4), (2, 0, 2), (2, 0, 3), (2, 0, 4), (3, 6, 5), (4, 0, 2), (4, 2, 0)]}
    keys = [(0, 2, 0)]
    locks = [(0, 2, 2)]
    arrows = {"r": [(0, 2, 4), (1, 6, 6)], "l": [(0, 0, 2)], "u": [], "d": [(0, 3, 6)], "h": [(0, 1, 6), (0, 4, 4), (0, 5, 6), (0, 6, 6)], "v": [(0, 0, 5)]}
    is_sat, is_passed_flat, order_array = solve_dice(height, width, depth, blocks, walls_h, walls_v, numbers, walls_edge, reds, letters, arrows, keys, locks, start, end)
    print("maze dice:", is_sat)
    if is_sat:
        print("dice_grid:")
        for s in range(6):
            print(f"surface {s}:")
            print(puz_util.stringify_array(order_array[s], lambda x: "XXX" if x == -1 else "???" if x == None else str(x).zfill(3)))

if __name__ == "__main__":
    print("----------")
    _main1()
    print("----------")
    _main2()
    print("----------")
    _main3()
    print("----------")
    _main4()
    print("----------")

    _main5()
    print("----------")

    _main_dice()
