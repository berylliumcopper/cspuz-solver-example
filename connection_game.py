from cspuz import graph, Solver, BoolGridFrame
from cspuz.constraints import count_true, fold_or, fold_and
from cspuz.puzzle import util
from cspuz.array import BoolArray2D, IntArray2D

def solve_connection_game(height, width, up, left, n_lines):
    solver = Solver()
    grid = solver.int_array((height, width), 0, n_lines-1)
    solver.add_answer_key(grid)
    frame = BoolGridFrame(solver, height-1, width-1)
    solver.add_answer_key(frame)
    paths = []
    for i in range(n_lines):
        path = BoolGridFrame(solver, height-1, width-1)
        passed = graph.active_edges_single_path(solver, path)
        paths.append(path)
        for y in range(height):
            for x in range(width):
                solver.ensure(passed[y, x] == (grid[y, x] == i))

    for y in range(height - 1):
        for x in range(width - 1):
            solver.ensure(~((grid[y, x] == grid[y+1, x]) & (grid[y, x] == grid[y, x+1]) & (grid[y, x] == grid[y+1, x+1])))
    
    for y in range(height-1):
        for x in range(width):
            solver.ensure(frame[2*y+1, 2*x] == fold_or([paths[i][2*y+1, 2*x] for i in range(n_lines)]))
            solver.ensure(frame[2*y+1, 2*x] == (grid[y, x] == grid[y+1, x]))
    for x in range(width-1):
        for y in range(height):
            solver.ensure(frame[2*y, 2*x+1] == fold_or([paths[i][2*y, 2*x+1] for i in range(n_lines)]))
            solver.ensure(frame[2*y, 2*x+1] == (grid[y, x] == grid[y, x+1]))

    for x in range(width):
        if len(up[x]) == 0:
            for y in range(height - 1):
                solver.ensure(grid[y, x] != grid[y+1, x])
        else:
            position = solver.int_array((len(up[x])), 0, height-up[x][-1])
            for i in range(len(up[x]) - 1):
                solver.ensure(position[i] + up[x][i] - 1 < position[i+1])
            for y in range(height - 1):
                j = fold_or([(y >= position[i]) & (y < position[i]+ up[x][i] - 1) for i in range(len(up[x]))])
                solver.ensure(j.then(frame[2*y+1, 2*x]))
                solver.ensure((~j).then(~frame[2*y+1, 2*x]))
    for y in range(height):
        if len(left[y]) == 0:
            for x in range(width - 1):
                solver.ensure(grid[y, x] != grid[y, x+1])
        else:
            position = solver.int_array((len(left[y])), 0, width-left[y][-1])
            for i in range(len(left[y]) - 1):
                solver.ensure(position[i] + left[y][i] - 1 < position[i+1])
            for x in range(width - 1):
                j = fold_or([(x >= position[i]) & (x < position[i]+ left[y][i] - 1) for i in range(len(left[y]))])
                solver.ensure(j.then(frame[2*y, 2*x+1]))
                solver.ensure((~j).then(~frame[2*y, 2*x+1]))
    solver.ensure(grid[4, 2] == grid[4, 3])

    is_sat = solver.solve()
    return is_sat, grid, frame

if __name__ == "__main__":
    
    height = 14
    width = 11
    up = [[12], [10], [9], [9], [5, 6], [3, 4], [2, 2], [2, 3], [3, 2], [5, 2, 2], [10, 3]]
    left =[[10], [9], [4, 4], [3, 2, 2], [2, 2, 2], [4], [6], [4], [4], [4], [2, 3], [2, 3], [2, 5], [2, 9]]
    n_lines = 12
    '''
    height = 5
    width = 4
    up = [[2, 3], [3], [3], [5]]
    left =[[3], [], [], [2], [4]]
    n_lines = 3
    '''
    is_sat, grid, frame = solve_connection_game(height, width, up, left, n_lines)
    print(is_sat)
    if is_sat:
        print(util.stringify_grid_frame(frame))