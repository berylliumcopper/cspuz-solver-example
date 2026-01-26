from cspuz import Solver, BoolGridFrame, graph
from cspuz.constraints import count_true, fold_or, fold_and
from cspuz.puzzle import util

def solve_samsung_galaxy(L, n_star, regions, centers):
    n_reg = len(regions)
    solver = Solver()
    answer = solver.int_array((L, L), 0, n_reg)
    stars = solver.bool_array((L, L))
    edge = BoolGridFrame(solver, L-1, L-1)
    solver.add_answer_key(answer)
    solver.add_answer_key(edge)

    for x in range(L):
        solver.ensure(count_true(stars[x, :]) == n_star)
        solver.ensure(count_true(stars[:, x]) == n_star)
    solver.ensure(~(stars[:-1, :] & stars[1:, :]))
    solver.ensure(~(stars[:, :-1] & stars[:, 1:]))
    solver.ensure(~(stars[:-1, :-1] & stars[1:, 1:]))
    solver.ensure(~(stars[:-1, 1:] & stars[1:, :-1]))

    for y in range(L):
        for x in range(L):
            solver.ensure(stars[y, x] == (answer[y, x] == 0))

    for y in range(L - 1):
        for x in range(L):
            solver.ensure(edge[y*2 + 1, x*2] == ~(answer[y, x] == answer[y + 1, x]))
    for y in range(L):
        for x in range(L - 1):
            solver.ensure(edge[y*2, x*2 + 1] == ~(answer[y, x] == answer[y, x + 1]))
    for i in range(n_reg):
        (cy, cx) = centers[i]
        for (y, x) in regions[i]:
            solver.ensure(answer[y, x] == i + 1)
        one = solver.bool_array((L, L))
        for y in range(L):
            for x in range(L):
                solver.ensure(one[y, x] == (answer[y, x] == i + 1))
                if cy - y < 0 or cy - y >= L or cx - x < 0 or cx - x >= L:
                    solver.ensure(one[y, x] == False)
                else:
                    solver.ensure(one[y, x] == one[cy - y, cx - x])
        graph.active_vertices_connected(solver, one)
    is_sat = solver.solve()
    return is_sat, answer, edge

def _main():
    centers = [(0, 3), (0, 19), (0, 26), (1, 8), (1, 14), (3, 10), (4, 3), (4, 6), (4, 14), (4, 20), (5, 26), \
            (6, 10), (6, 22), (8, 12), (8, 28), (10, 1), (10, 5), (10, 20), (10, 26), (12, 0), (12, 25), (14, 4), \
            (14, 8), (14, 22), (15, 11), (15, 18), (15, 24), (16, 0), (16, 6), (16, 14), (18, 6), (19, 15), (20, 8), \
            (20, 10), (20, 26), (21, 0), (22, 7), (22, 17), (23, 14), (23, 20), (24, 2), (24, 6), (24, 17), (24, 22), \
            (24, 28), (25, 10), (26, 5), (26, 17), (27, 12), (27, 20), (27, 24), (28, 6), (28, 15), (28, 27)]
    regions = []
    for (y, x) in centers:
        sx = []
        sy = []
        if x % 2 == 0:
            sx.append(x//2)
        else:
            sx.append((x-1)//2)
            sx.append((x+1)//2)
        if y % 2 == 0:
            sy.append(y//2)
        else:
            sy.append((y-1)//2)
            sy.append((y+1)//2)
        regions.append([(yy, xx) for yy in sy for xx in sx])
    print(regions)
    is_sat, answer, edge = solve_samsung_galaxy(15, 3, regions, centers)
    print(is_sat)
    if is_sat:
        print(util.stringify_array(answer, str))
        print(util.stringify_grid_frame(edge).replace('-', 'f').replace('|', '-').replace('f', '|').replace('x', ' '))

if __name__ == "__main__":
    _main()