import sys
import os
sys.path.insert(0, os.path.abspath("cspuz"))

from cspuz import graph, Solver, BoolGridFrame
from cspuz.graph import Graph
from cspuz.array import BoolArray2D, IntArray2D
from cspuz.constraints import alldifferent, count_true, cond
from cspuz.puzzle import util

def sum_neighbors(grid_frame, index_array, height, width, y, x):
    return (0 if y == 0 else (grid_frame.vertical[y-1, x]).cond(index_array[y - 1, x], 0)) + (0 if y == height - 1 else (grid_frame.vertical[y, x]).cond(index_array[y + 1, x], 0)) + (0 if x == 0 else (grid_frame.horizontal[y, x-1]).cond(index_array[y, x - 1], 0)) + (0 if x == width - 1 else (grid_frame.horizontal[y, x]).cond(index_array[y, x + 1], 0))

'''
simplepath rule:
The path passes through each unshaded cell (marked with '1' in grid) exactly once, and does not pass through any shaded cell (marked with '0' in grid).
The path starts at the start cell and ends at the end cell.
At each cell, the path can move to the adjacent cell in the four cardinal directions (up, down, left, right).

order:
The integer array index_array[y, x] is the order that the path passes through each cell (y, x), -1 if the cell is unvisited, and 0,1,2,3,... as the path starts from the start cell.
'''

def solve_simplepath_order(height, width, grid, start, end):
    solver = Solver()

    grid_frame = BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(grid_frame)
    path = graph.active_edges_single_path(solver, grid_frame)
    for y in range(height):
        for x in range(width):
            if grid[y][x] == 0:
                solver.ensure(path[y, x] == False)
            else:
                solver.ensure(path[y, x] == True)
    
    solver.ensure(count_true(grid_frame.vertex_neighbors(start)) == 1)
    solver.ensure(count_true(grid_frame.vertex_neighbors(end)) == 1)

    index_array = solver.int_array((height, width), -1, height * width - 1)
    solver.add_answer_key(index_array)
    for y in range(height):
        for x in range(width):
            if grid[y][x] == 1 and (y, x) != start and (y, x) != end:
                solver.ensure(index_array[y, x] + index_array[y, x] == sum_neighbors(grid_frame, index_array, height, width, y, x))
                solver.ensure(index_array[y, x] > 0)
            if grid[y][x] == 0:
                solver.ensure(index_array[y, x] == -1)
            elif (y, x) == start:
                solver.ensure(index_array[y, x] == 0)

    if start[0] != 0:
        solver.ensure(index_array[start[0]-1, start[1]] <= grid_frame.vertical[start[0]-1, start[1]].cond(1, height*width - 1))
    if start[1] != 0:
        solver.ensure(index_array[start[0], start[1]-1] <= grid_frame.horizontal[start[0], start[1]-1].cond(1, height*width - 1))
    if start[0] != height - 1:
        solver.ensure(index_array[start[0]+1, start[1]] <= grid_frame.vertical[start[0], start[1]].cond(1, height*width - 1))
    if start[1] != width - 1:
        solver.ensure(index_array[start[0], start[1]+1] <= grid_frame.horizontal[start[0], start[1]].cond(1, height*width - 1))

    is_sat = solver.solve()
    return is_sat, grid_frame, index_array

def _main():
    height = 6
    width = 6
    
    start = (0, 3)
    end = (5, 3)
    grid = [[1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 0, 1, 1, 0],
            [1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1]]
    is_sat, grid_frame, index_array = solve_simplepath_order(height, width, grid, start, end)
    print(is_sat)
    if is_sat:
        print("grid_frame:")
        print(util.stringify_grid_frame(grid_frame))
        print("index_array:")
        print(util.stringify_array(index_array, lambda x: "XX" if x == -1 else "??" if x == None else str(x).zfill(2)))

if __name__ == "__main__":
    _main()
