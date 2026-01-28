from cspuz import Solver, BoolGridFrame, graph
from cspuz.constraints import count_true, fold_or, fold_and
from cspuz.puzzle import util
from util import get_pathlength

def solve_unbengable_loop(L, regions):
    solver = Solver()
    grid = BoolGridFrame(solver, L-1, L-1)
    solver.add_answer_key(grid)
    is_passed = graph.active_edges_single_cycle(solver, grid)
    for y in range(L):
        for x in range(L):
            solver.ensure(is_passed[y, x])

    is_white = solver.bool_array((L, L))
    is_black = solver.bool_array((L, L))
    solver.add_answer_key(is_white)
    solver.add_answer_key(is_black)
    for i in range(L):
        solver.ensure(count_true(is_white[i, :]) == 1)
        solver.ensure(count_true(is_white[:, i]) == 1)
        solver.ensure(count_true(is_black[i, :]) == 1)
        solver.ensure(count_true(is_black[:, i]) == 1)
    solver.ensure(~(is_white[:, :] & is_black[:, :]))
    solver.ensure(~(is_white[:-1, :] & is_white[1:, :]))
    solver.ensure(~(is_white[:, :-1] & is_white[:, 1:]))
    solver.ensure(~(is_white[:-1, :-1] & is_white[1:, 1:]))
    solver.ensure(~(is_white[:-1, 1:] & is_white[1:, :-1]))
    solver.ensure(~(is_black[:-1, :] & is_black[1:, :]))
    solver.ensure(~(is_black[:, :-1] & is_black[:, 1:]))
    solver.ensure(~(is_black[:-1, :-1] & is_black[1:, 1:]))
    solver.ensure(~(is_black[:-1, 1:] & is_black[1:, :-1]))

    to_up, to_down, to_left, to_right = get_pathlength(solver, grid, L, L)

    for y in range(L):
        for x in range(L):
            solver.ensure((~is_white[y, x]) | (((to_up[y, x] == 1) & (to_down[y, x] >= 1)) | ((to_up[y, x] >= 1) & (to_down[y, x] == 1)) \
                                            | ((to_left[y, x] == 1) & (to_right[y, x] >= 1)) | ((to_left[y, x] >= 1) & (to_right[y, x] == 1))))
            solver.ensure((~is_black[y, x]) | (((to_up[y, x] > 1) & (to_left[y, x] > 1)) | ((to_up[y, x] > 1) & (to_right[y, x] > 1)) \
                                            | ((to_down[y, x] > 1) & (to_left[y, x] > 1)) | ((to_down[y, x] > 1) & (to_right[y, x] > 1))))

    for i in regions:
        pos, pair = i
        r_white = []
        r_black = []
        for (y, x) in pos:
            r_white.append(is_white[y, x])
            r_black.append(is_black[y, x])
        solver.ensure(count_true(r_white) == 1)
        solver.ensure(count_true(r_black) == 1)
        for (a, b) in pair:
            (ya, xa) = a
            (yb, xb) = b
            solver.ensure(~(is_white[ya, xa] & is_black[yb, xb]))
            solver.ensure(~(is_black[ya, xa] & is_white[yb, xb]))

    is_sat = solver.solve()
    return is_sat, grid, is_white, is_black

def _main():
    board = [[0,0,1,1,1,0,0,2,2,2,2,2], \
             [0,1,1,1,0,0,0,2,3,3,2,2], \
             [0,0,0,0,0,2,2,2,2,3,3,2], \
             [2,2,2,2,2,2,2,2,2,2,2,2], \
             [2,2,2,4,4,4,4,4,2,5,5,2], \
             [6,2,2,4,4,7,7,4,4,4,5,5], \
             [6,2,2,7,7,7,7,4,4,4,4,4], \
             [6,2,7,7,7,7,8,9,9,4,4,4], \
             [6,2,2,10,7,7,8,11,9,9,4,4], \
             [6,6,2,10,7,8,8,11,11,11,11,4], \
             [6,6,10,10,10,8,4,11,4,4,4,4], \
             [6,6,10,10,10,4,4,4,4,4,4,4]]
    pos = []
    pair = []
    for i in range(12):
        one_pos = []
        for y in range(12):
            for x in range(12):
                if board[y][x] == i:
                    one_pos.append((y, x))
        pos.append(one_pos)
        one_pair = []
        for j in range(len(one_pos)):
            for k in range(j):
                (jy, jx) = one_pos[j]
                (ky, kx) = one_pos[k]
                if abs(jy - ky) <= 1 and abs(jx - kx) <= 1:
                    one_pair.append((one_pos[j], one_pos[k]))
        pair.append(one_pair)
    problem = []
    for i in range(len(pos)):
        problem.append((pos[i], pair[i]))
    is_sat, grid, is_white, is_black = solve_unbengable_loop(12, problem)
    print(is_sat)
    if is_sat:
        print(util.stringify_grid_frame(grid))
        whitestr = list(util.stringify_array(is_white, str).replace('True', 'W').replace('False', '.').replace(' ', ''))
        blackstr = list(util.stringify_array(is_black, str).replace('True', 'B').replace('False', '.').replace(' ', ''))
        whitestr.append('\n')
        blackstr.append('\n')
        totalstr = []
        for y in range(12):
            for x in range(13):
                if x != 0:
                    totalstr.append(' ')
                if whitestr[y*13 + x] == 'W':
                    totalstr.append('W')
                elif blackstr[y*13 + x] == 'B':
                    totalstr.append('B')
                elif x == 12:
                    totalstr.append('\n')
                else:
                    totalstr.append('.')
        print(''.join(totalstr))

if __name__ == "__main__":
    _main()