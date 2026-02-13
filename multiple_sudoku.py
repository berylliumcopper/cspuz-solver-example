from cspuz import graph, Solver, count_true, BoolGridFrame
from cspuz.puzzle import util as puz_util
from cspuz.constraints import count_true, fold_or, alldifferent

def solve_multiple_sudoku(grid, nonogram_l, nonogram_u, n_path):
    solver = Solver()

    sudoku_grid = solver.int_array((9, 9), 1, 9)
    solver.add_answer_key(sudoku_grid)
    for y in range(9):
        for x in range(9):
            if grid[y][x] != 0:
                solver.ensure(sudoku_grid[y, x] == grid[y][x])
    for y in range(9):
        solver.ensure(alldifferent(sudoku_grid[y, :])) # row
    for x in range(9):
        solver.ensure(alldifferent(sudoku_grid[:, x])) # column
    for y in range(3):
        for x in range(3):
            solver.ensure(alldifferent(sudoku_grid[y * 3 : (y + 1) * 3, x * 3 : (x + 1) * 3]))

    green = solver.bool_array((9, 9))
    red = solver.bool_array((9, 9))
    solver.add_answer_key(green)
    solver.add_answer_key(red)
    for y in range(9):
        for x in range(9):
            solver.ensure((~green[y, x]) | (~red[y, x]))
    
    for y in range(9):
        len_nonogram_l = len(nonogram_l[y])
        nonogram_numbers = solver.int_array((9, len_nonogram_l + 2), -9, 9)
        solver.ensure(nonogram_numbers[0, 0] == green[y, 0].cond(1, red[y, 0].cond(-1, 0)))
        for i in range(1, len_nonogram_l + 2):
            solver.ensure(nonogram_numbers[0, i] == 0)
        for x in range(1, 9):
            solver.ensure(nonogram_numbers[x, 0] == (((green[y, x] == green[y, x-1]) & (red[y, x] == red[y, x-1])) | (nonogram_numbers[x-1, 0] == 0)).cond(nonogram_numbers[x-1, 0], 0) + green[y, x].cond(1, red[y, x].cond(-1, 0)))
            for i in range(1, len_nonogram_l + 2):
                solver.ensure(nonogram_numbers[x, i] == (((green[y, x] == green[y, x-1]) & (red[y, x] == red[y, x-1])) | (nonogram_numbers[x-1, 0] == 0)).cond(nonogram_numbers[x-1, i], nonogram_numbers[x-1, i-1]))

        for i in range(len_nonogram_l):
            solver.ensure(nonogram_l[y][i] == (green[y, 8] | red[y, 8]).cond(nonogram_numbers[8, i], nonogram_numbers[8, i+1]))
        solver.ensure(nonogram_numbers[8, len_nonogram_l + 1] == 0)
        solver.ensure((green[y, 8] | red[y, 8]).cond(nonogram_numbers[8, len_nonogram_l], nonogram_numbers[8, 0]) == 0)

    
    for x in range(9):
        len_nonogram_u = len(nonogram_u[x])
        nonogram_numbers = solver.int_array((9, len_nonogram_u + 2), -9, 9)
        solver.ensure(nonogram_numbers[0, 0] == green[0, x].cond(1, red[0, x].cond(-1, 0)))
        for i in range(1, len_nonogram_u + 2):
            solver.ensure(nonogram_numbers[0, i] == 0)
        for y in range(1, 9):
            solver.ensure(nonogram_numbers[y, 0] == (((green[y, x] == green[y-1, x]) & (red[y, x] == red[y-1, x])) | (nonogram_numbers[y-1, 0] == 0)).cond(nonogram_numbers[y-1, 0], 0) + green[y, x].cond(1, red[y, x].cond(-1, 0)))
            for i in range(1, len_nonogram_u + 2):
                solver.ensure(nonogram_numbers[y, i] == (((green[y, x] == green[y-1, x]) & (red[y, x] == red[y-1, x])) | (nonogram_numbers[y-1, 0] == 0)).cond(nonogram_numbers[y-1, i], nonogram_numbers[y-1, i-1]))

        for i in range(len_nonogram_u):
            solver.ensure(nonogram_u[x][i] == (green[8, x] | red[8, x]).cond(nonogram_numbers[8, i], nonogram_numbers[8, i+1]))
        solver.ensure(nonogram_numbers[8, len_nonogram_u + 1] == 0)
        solver.ensure((green[8, x] | red[8, x]).cond(nonogram_numbers[8, len_nonogram_u], nonogram_numbers[8, 0]) == 0)

    path_lengths = solver.int_array(n_path, 1, 9)

    path_grid = solver.int_array((9, 9), 0, n_path - 1)
    for i in range(n_path):
        solver.ensure(count_true(path_grid == i) == path_lengths[i] + 1)
        one_path_frame = BoolGridFrame(solver, 8, 8)
        one_path = graph.active_edges_single_path(solver, one_path_frame)
        solver.ensure(count_true(one_path[:, :] & green[:, :]) == 1)
        solver.ensure(count_true(one_path[:, :] & red[:, :]) == 1)
        for y in range(9):
            for x in range(9):
                solver.ensure(one_path[y, x] == (path_grid[y, x] == i))
                solver.ensure(one_path[y, x].then(count_true(one_path_frame.vertex_neighbors((y, x))) == (green[y, x] | red[y, x]).cond(1, 2)))
                solver.ensure((one_path[y, x] & green[y, x]).then(path_lengths[i] == sudoku_grid[y, x]))

    solver.solve()
    
    is_sat = solver.solve()
    return is_sat, sudoku_grid


def _main():
    grid = [
        [0, 4, 0, 0, 3, 7, 6, 0, 0],
        [0, 0, 0, 4, 5, 0, 0, 8, 0],
        [0, 0, 0, 0, 2, 0, 0, 0, 0],
        [4, 6, 8, 0, 0, 5, 9, 0, 0],
        [0, 3, 9, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 7, 0, 0, 0, 0, 4],
        [0, 0, 0, 0, 4, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    nonogram_l = [
        [1, 1],
        [-1, 1, 1],
        [1, -1, -1, 1],
        [-1],
        [-1, 1],
        [-1, -1],
        [1, 1],
        [-1, 1, 1, -1, 1],
        [-1, -2]
    ]
    nonogram_u = [
        [2, 1, 3],
        [-1],
        [2],
        [-1, 1],
        [1],
        [-1, -1],
        [-1, -2],
        [1, -2],
        [-2, -1, 1]
    ]
    n_path = 12
    is_sat, sudoku_grid = solve_multiple_sudoku(grid, nonogram_l, nonogram_u, n_path)
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(sudoku_grid, dict([(None, "?")] + [(i, str(i)) for i in range(1, 10)])))

if __name__ == "__main__":
    _main()
