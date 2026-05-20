from cspuz import graph, Solver, count_true, BoolGridFrame
from cspuz.puzzle import util as puz_util
from util import get_direction_order, get_pathlength
from cspuz.array import BoolArray1D, IntArray1D, IntArray2D
from cspuz.constraints import count_true, fold_or, fold_and, alldifferent

def solve_between_canvas1(grid, red, orange, blue, green):
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
    
    even_first = []
    odd_first = []
    for idx, pt in enumerate(red):
        if idx % 2 == 0:
            even_first.append((sudoku_grid[pt] == 2)|(sudoku_grid[pt] == 4)|(sudoku_grid[pt] == 6)|(sudoku_grid[pt] == 8))
            odd_first.append((sudoku_grid[pt] == 1)|(sudoku_grid[pt] == 3)|(sudoku_grid[pt] == 5)|(sudoku_grid[pt] == 7)|(sudoku_grid[pt] == 9))
        else:
            even_first.append((sudoku_grid[pt] == 1)|(sudoku_grid[pt] == 3)|(sudoku_grid[pt] == 5)|(sudoku_grid[pt] == 7)|(sudoku_grid[pt] == 9))
            odd_first.append((sudoku_grid[pt] == 2)|(sudoku_grid[pt] == 4)|(sudoku_grid[pt] == 6)|(sudoku_grid[pt] == 8))
    solver.ensure(fold_and(even_first) | fold_and(odd_first))

    for idx in range(len(orange) - 1):
        solver.ensure((sudoku_grid[orange[idx]] - sudoku_grid[orange[idx + 1]] >= 4)|(sudoku_grid[orange[idx]] - sudoku_grid[orange[idx + 1]] <= -4))
    
    totals = []
    for ls in blue:
        total = 0
        for pt in ls:
            total += sudoku_grid[pt]
        totals.append(total)
    for idx in range(len(blue) - 1):
        solver.ensure(totals[idx] == totals[idx + 1])
    
    for idx in range(len(green) - 1):
        solver.ensure((sudoku_grid[green[idx]] - sudoku_grid[green[idx + 1]] >= 5)|(sudoku_grid[green[idx]] - sudoku_grid[green[idx + 1]] <= -5))
    

    is_sat = solver.solve()
    return is_sat, sudoku_grid

def _main1():
    grid = [
        [1, 5, 3, 8, 0, 0, 0, 4, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 6],
        [0, 0, 0, 0, 0, 2, 1, 0, 8],
        [0, 0, 0, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 5, 0, 0, 0],
        [0, 0, 9, 0, 0, 0, 0, 0, 0],
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 2, 0, 0, 0, 8, 6, 7, 3]
    ]
    red = [(1, 7), (0, 7), (0, 6), (0, 5), (1, 4), (2, 4), (3, 4)]
    orange = [(4, 5), (4, 6), (4, 7), (5, 8), (6, 8), (7, 8), (7, 7)]
    blue = [[(5, 4)], [(6, 4), (7, 4), (8, 3)], [(8, 2), (8, 1), (7, 1)]]
    green = [(1, 1), (1, 0), (2, 0), (3, 0), (4, 1), (4, 2), (4, 3)]
    is_sat, sudoku_grid = solve_between_canvas1(grid, red, orange, blue, green)
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(sudoku_grid, dict([(None, "?")] + [(i, str(i)) for i in range(1, 10)])))

def solve_between_canvas2(grid, lines):
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

    for l in lines:
        n_l = len(l)
        for i in range(n_l):
            solver.ensure(sudoku_grid[l[i]] == sudoku_grid[l[n_l - 1 - i]])

    is_sat = solver.solve()
    return is_sat, sudoku_grid

def _main2():
    grid = [
        [1, 5, 3, 8, 0, 0, 0, 4, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 6],
        [0, 0, 0, 0, 0, 2, 1, 0, 8],
        [0, 0, 0, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 5, 0, 0, 0],
        [0, 0, 9, 0, 0, 0, 0, 0, 0],
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 2, 0, 0, 0, 8, 6, 7, 3]
    ]
    lines = [[(1, 7), (0, 7), (0, 6), (0, 5), (1, 4), (2, 4), (3, 4)], [(4, 5), (4, 6), (4, 7), (5, 8), (6, 8), (7, 8), (7, 7)], [(5, 4), (6, 4), (7, 4), (8, 3), (8, 2), (8, 1), (7, 1)], [(1, 1), (1, 0), (2, 0), (3, 0), (4, 1), (4, 2), (4, 3)]]
    is_sat, sudoku_grid = solve_between_canvas2(grid, lines)
    print(is_sat)
    if is_sat:
        print(puz_util.stringify_array(sudoku_grid, dict([(None, "?")] + [(i, str(i)) for i in range(1, 10)])))

if __name__ == "__main__":
    _main2()