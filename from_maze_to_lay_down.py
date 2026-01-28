from cspuz.expr import BoolExpr, IntExpr, Expr
from cspuz.graph import Graph, active_edges_single_path
from cspuz.solver import Solver
from cspuz import graph, count_true, BoolGridFrame
from cspuz.puzzle import util

def sum_neighbors(grid_frame, index_array, height, width, y, x):
    return (0 if y == 0 else (grid_frame.vertical[y-1, x]).cond(index_array[y - 1, x], 0)) + (0 if y == height - 1 else (grid_frame.vertical[y, x]).cond(index_array[y + 1, x], 0)) + (0 if x == 0 else (grid_frame.horizontal[y, x-1]).cond(index_array[y, x - 1], 0)) + (0 if x == width - 1 else (grid_frame.horizontal[y, x]).cond(index_array[y, x + 1], 0))

def direction(solver,grid, is_passed, height, width, start, end):
    grid_rd = BoolGridFrame(solver, height - 1, width - 1)
    grid_lu = BoolGridFrame(solver, height - 1, width - 1)
    solver.ensure(((~grid.horizontal[:,:]) & (~grid_rd.horizontal[:,:]) & (~grid_lu.horizontal[:,:])) | ((grid.horizontal[:,:]) & (grid_rd.horizontal[:,:]) & (~grid_lu.horizontal[:,:])) | ((grid.horizontal[:,:]) & (~grid_rd.horizontal[:,:]) & (grid_lu.horizontal[:,:])))
    solver.ensure(((~grid.vertical[:,:]) & (~grid_rd.vertical[:,:]) & (~grid_lu.vertical[:,:])) | ((grid.vertical[:,:]) & (grid_rd.vertical[:,:]) & (~grid_lu.vertical[:,:])) | ((grid.vertical[:,:]) & (~grid_rd.vertical[:,:]) & (grid_lu.vertical[:,:])))
    
    for y in range(height):
        for x in range(width):
            if (y, x) != end:
                neighbors = []
                if y > 0:
                    neighbors.append(grid_lu.vertical[y - 1, x])
                if y < height - 1:
                    neighbors.append(grid_rd.vertical[y, x])
                if x > 0:
                    neighbors.append(grid_lu.horizontal[y, x - 1])
                if x < width - 1:
                    neighbors.append(grid_rd.horizontal[y, x])
                solver.ensure(count_true(neighbors) == is_passed[y, x].cond(1, 0))
    
    return grid_rd, grid_lu



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

    order_array = solver.int_array((height, width), -1, height * width - 1)
    solver.add_answer_key(order_array)

    grid_rd, grid_lu = direction(solver, grid, is_passed, height, width, start, end)

    for y in range(height):
        for x in range(width):
            if (y, x) == start:
                solver.ensure(order_array[y, x] == 0)
            elif (y, x) != end:
                solver.ensure(-1 == is_passed[y, x].cond(-1, order_array[y, x]))
    
    for y in range(height - 1):
        for x in range(width):
            solver.ensure(1 == grid_rd.vertical[y, x].cond(order_array[y + 1, x] - order_array[y, x], 1))
            solver.ensure(1 == grid_lu.vertical[y, x].cond(order_array[y, x] - order_array[y + 1, x], 1))
    
    for y in range(height):
        for x in range(width - 1):
            solver.ensure(1 == grid_rd.horizontal[y, x].cond(order_array[y, x + 1] - order_array[y, x], 1))
            solver.ensure(1 == grid_lu.horizontal[y, x].cond(order_array[y, x] - order_array[y, x + 1], 1))
    
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
        print(util.stringify_grid_frame(grid))
        print("order_array:")
        print(util.stringify_array(order_array, lambda x: "XXX" if x == -1 else "???" if x == None else str(x).zfill(3)))



if __name__ == "__main__":
    _main1()