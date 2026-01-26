from cspuz import Solver, BoolGridFrame, graph
from cspuz.constraints import count_true, fold_or
from cspuz.puzzle import util

def solve_star_rail(height, width, problem, stars=0):
    solver = Solver()
    loop = BoolGridFrame(solver, height - 1, width - 1)
    is_passed = graph.active_edges_single_cycle(solver, loop)
    rooms, clues = problem
    solver.add_answer_key(loop)
    solver.add_answer_key(is_passed)
    to_up = solver.int_array((height, width), 0, height - 1)
    to_down = solver.int_array((height, width), 0, height - 1)
    to_left = solver.int_array((height, width), 0, width - 1)
    to_right = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_up[0, :] == 0)
    for y in range(height):
        for x in range(width):
            if y == 0:
                solver.ensure(to_up[y, x] == 0)
            else:
                solver.ensure(to_up[y, x] == (loop[y * 2 - 1, x * 2].cond(to_up[y - 1, x] + 1, 0)))
            if y == height - 1:
                solver.ensure(to_down[y, x] == 0)
            else:
                solver.ensure(to_down[y, x] == (loop[y * 2 + 1, x * 2].cond(to_down[y + 1, x] + 1, 0)))
            if x == 0:
                solver.ensure(to_left[y, x] == 0)
            else:
                solver.ensure(to_left[y, x] == (loop[y * 2, x * 2 - 1].cond(to_left[y, x - 1] + 1, 0)))
            if x == width - 1:
                solver.ensure(to_right[y, x] == 0)
            else:
                solver.ensure(to_right[y, x] == (loop[y * 2, x * 2 + 1].cond(to_right[y, x + 1] + 1, 0)))
    for y in range(height):
        unpassed = []
        for x in range(width):
            unpassed.append(~is_passed[y, x])
        solver.ensure(count_true(unpassed) == stars)
    for x in range(width):
        unpassed = []
        for y in range(height):
            unpassed.append(~is_passed[y, x])
        solver.ensure(count_true(unpassed) == stars)
    m = len(clues)
    L = max(height, width)
    for i in range(m):
        unpassed = []
        for (y, x) in rooms[i]:
            unpassed.append(~is_passed[y, x])
        solver.ensure(count_true(unpassed) == stars)
    for y in range(height):
        for x in range(width):
            if y+1 < height:
                solver.ensure((~is_passed[y, x]).then(is_passed[y+1, x]))
            if y+1 < height and x-1 >= 0:
                solver.ensure((~is_passed[y, x]).then(is_passed[y+1, x-1]))
            if y+1 < height and x+1 < width:
                solver.ensure((~is_passed[y, x]).then(is_passed[y+1, x+1]))
            if x+1 < width:
                solver.ensure((~is_passed[y, x]).then(is_passed[y, x+1]))
    for i in range(m):
        if clues[i] == []:
            continue
        blen = solver.bool_array(L)
        for l in range(1, L):
            cond = []
            for (y, x) in rooms[i]:
                cond.append((to_left[y, x] + to_right[y, x]) == l)
                cond.append((to_up[y, x] + to_down[y, x]) == l)
            solver.ensure(blen[l] == fold_or(cond))
        for y in clues[i]:
            solver.ensure(blen[y])
        solver.ensure(count_true(blen[1:]) == len(clues[i]))
    is_sat = solver.solve()
    return is_sat, is_passed, loop
