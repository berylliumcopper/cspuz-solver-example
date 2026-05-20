from cspuz.grid_frame import BoolGridFrame
from cspuz.array import BoolArray2D, IntArray2D
from cspuz.solver import Solver
from cspuz.expr import IntExpr
from typing import Tuple
from cspuz.constraints import count_true

def sum_neighbors(grid_frame: BoolGridFrame, index_array: IntArray2D, height: int, width: int, y: int, x: int) -> IntExpr:
    return (0 if y == 0 else (grid_frame.vertical[y-1, x]).cond(index_array[y - 1, x], 0)) + (0 if y == height - 1 else (grid_frame.vertical[y, x]).cond(index_array[y + 1, x], 0)) + (0 if x == 0 else (grid_frame.horizontal[y, x-1]).cond(index_array[y, x - 1], 0)) + (0 if x == width - 1 else (grid_frame.horizontal[y, x]).cond(index_array[y, x + 1], 0))

def get_direction_order(solver: Solver, grid: BoolGridFrame, is_passed: BoolArray2D, height: int, width: int, start: Tuple[int, int], end: Tuple[int, int]) -> Tuple[BoolGridFrame, BoolGridFrame, IntArray2D]:
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
                solver.ensure(is_passed[y, x].then(count_true(neighbors) == 1))

    order_array = solver.int_array((height, width), -1, height * width - 1)
    solver.add_answer_key(order_array)

    for y in range(height):
        for x in range(width):
            if (y, x) == start:
                solver.ensure(order_array[y, x] == 0)
            elif (y, x) != end:
                solver.ensure((~is_passed[y, x]).then(order_array[y, x] == -1))
    
    for y in range(height - 1):
        for x in range(width):
            solver.ensure(grid_rd.vertical[y, x].then(order_array[y + 1, x] - order_array[y, x] == 1))
            solver.ensure(grid_lu.vertical[y, x].then(order_array[y, x] - order_array[y + 1, x] == 1))
    
    for y in range(height):
        for x in range(width - 1):
            solver.ensure(grid_rd.horizontal[y, x].then(order_array[y, x + 1] - order_array[y, x] == 1))
            solver.ensure(grid_lu.horizontal[y, x].then(order_array[y, x] - order_array[y, x + 1] == 1))
    
    return grid_rd, grid_lu, order_array

def get_pathlength(solver: Solver, grid: BoolGridFrame, height: int, width: int) -> Tuple[IntArray2D, IntArray2D, IntArray2D, IntArray2D]:
    to_up = solver.int_array((height, width), 0, height - 1)
    to_down = solver.int_array((height, width), 0, height - 1)
    to_left = solver.int_array((height, width), 0, width - 1)
    to_right = solver.int_array((height, width), 0, width - 1)
    for y in range(height):
        for x in range(width):
            if y == 0:
                solver.ensure(to_up[y, x] == 0)
            else:
                solver.ensure(to_up[y, x] == (grid.vertical[y - 1, x].cond(to_up[y - 1, x] + 1, 0)))
            if y == height - 1:
                solver.ensure(to_down[y, x] == 0)
            else:
                solver.ensure(to_down[y, x] == (grid.vertical[y, x].cond(to_down[y + 1, x] + 1, 0)))
            if x == 0:
                solver.ensure(to_left[y, x] == 0)
            else:
                solver.ensure(to_left[y, x] == (grid.horizontal[y, x - 1].cond(to_left[y, x - 1] + 1, 0)))
            if x == width - 1:
                solver.ensure(to_right[y, x] == 0)
            else:
                solver.ensure(to_right[y, x] == (grid.horizontal[y, x].cond(to_right[y, x + 1] + 1, 0)))
    return to_up, to_down, to_left, to_right
