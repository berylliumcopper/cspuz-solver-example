import sys
import os
sys.path.insert(0, os.path.abspath("cspuz"))

from cspuz import graph, Solver, BoolGridFrame
from cspuz.graph import Graph
from cspuz.array import BoolArray2D
from cspuz.constraints import alldifferent, count_true, cond
from cspuz.puzzle import util
from itertools import permutations

class BoolKnightFrame:
    """
    A frame representing a knight's graph on a grid of size height x width.
    Edges exist between cells (y1, x1) and (y2, x2) if they are a knight's move apart.
    """
    def __init__(self, solver, height, width):
        self.solver = solver
        self.height = height
        self.width = width
        
        # Define vertices as (y, x) tuples
        self.vertices = [(y, x) for y in range(height) for x in range(width)]
        self.v_map = {v: i for i, v in enumerate(self.vertices)}
        
        # Find all knight move edges
        self.edges = []
        for y in range(height):
            for x in range(width):
                # Possible knight moves
                moves = [
                    (y + 1, x + 2), (y + 1, x - 2), (y - 1, x + 2), (y - 1, x - 2),
                    (y + 2, x + 1), (y + 2, x - 1), (y - 2, x + 1), (y - 2, x - 1)
                ]
                for ny, nx in moves:
                    # To avoid double adding undirected edges, only add if (y, x) < (ny, nx)
                    if 0 <= ny < height and 0 <= nx < width:
                        if (y, x) < (ny, nx):
                            self.edges.append(((y, x), (ny, nx)))
        
        self.graph = Graph(len(self.vertices))
        for u, v in self.edges:
            self.graph.add_edge(self.v_map[u], self.v_map[v])
            
        # Create boolean variables for each edge
        self.edge_vars = solver.bool_array(len(self.edges))

    def __iter__(self):
        """
        Iterate over the boolean variables associated with the edges.
        """
        return iter(self.edge_vars)

    def vertex_neighbors(self, y, x=None):
        """
        Returns a BoolArray1D of edge variables incident to the vertex (y, x).
        """
        if x is None:
            y, x = y
        v_idx = self.v_map[(y, x)]
        from cspuz.array import BoolArray1D
        return BoolArray1D([self.edge_vars[edge_id] for _, edge_id in self.graph.incident_edges[v_idx]])

    def active_edges_single_path(self):
        """
        Add a constraint that the active edges form a single path.
        Returns a BoolArray2D representing whether each cell is passed by the path.
        """
        is_passed_flat = graph.active_edges_single_path(self.solver, self.edge_vars, self.graph)
        return is_passed_flat.reshape((self.height, self.width))

    def stringify_vertex_adjacencies(self) -> str:
        """
        List each cell and the status of knight moves connected to it.
        Format: (y, x): (y1, x1)[status] (y2, x2)[status] ...
        Status: 'V' for True, 'X' for False, ' ' for None.
        """
        res = []
        for i, v_coord in enumerate(self.vertices):
            line = [f"{v_coord}:"]
            for neighbor_idx, edge_id in self.graph.incident_edges[i]:
                neighbor_coord = self.vertices[neighbor_idx]
                sol = self.edge_vars[edge_id].sol
                status = 'V' if sol is True else ('X' if sol is False else ' ')
                line.append(f"{neighbor_coord}{status}")
            res.append(" ".join(line))
        return "\n".join(res)

    def stringify_paths_and_loops(self) -> str:
        """
        Find and represent all paths and loops formed by active knight moves.
        Only works if there are no branches (degree <= 2 for all cells).
        """
        adj = {}
        for i, (u_idx, v_idx) in enumerate(self.graph.edges):
            if self.edge_vars[i].sol is True:
                u_coord = self.vertices[u_idx]
                v_coord = self.vertices[v_idx]
                if u_coord not in adj: adj[u_coord] = []
                if v_coord not in adj: adj[v_coord] = []
                adj[u_coord].append(v_coord)
                adj[v_coord].append(u_coord)
        
        for coord, neighbors in adj.items():
            if len(neighbors) > 2:
                return "Knight graph contains branches (degree > 2). Cannot represent as simple paths/loops."

        visited = set()
        results = []

        # Find paths (start from cells with degree 1)
        endpoints = [v for v, neighbors in adj.items() if len(neighbors) == 1]
        for start_node in endpoints:
            if start_node not in visited:
                path = []
                curr = start_node
                while curr is not None and curr not in visited:
                    visited.add(curr)
                    path.append(str(curr))
                    next_node = None
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            next_node = neighbor
                            break
                    curr = next_node
                results.append("path: " + " ".join(path))

        # Find loops (remaining active cells must have degree 2)
        for start_node in list(adj.keys()):
            if start_node not in visited:
                loop = []
                curr = start_node
                while curr not in visited:
                    visited.add(curr)
                    loop.append(str(curr))
                    next_node = None
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            next_node = neighbor
                            break
                    if next_node is None: # Loop closed
                        break
                    curr = next_node
                results.append("loop: " + " ".join(loop))

        return "\n".join(results)

def encode(i, width):
    return i[0] * width + i[1]

'''
knight_tour rule:
The path passes through each unshaded cell (marked with '1' in grid) exactly once, and does not pass through any shaded cell (marked with '0' in grid).
At each knight cell, the path switches from orthogonal move to knight move (two steps in one direction and one step in the other direction) or vice versa.
The path starts at the start cell and ends at the end cell.
'''

def solve_knight_tour(height, width, start, end, grid, knights):
    solver = Solver()
    n_knights = len(knights)//2 + len(knights)%2
    n_non_knights = len(knights)//2 + 1
    knight_frames = [BoolKnightFrame(solver, height, width) for _ in range(n_knights)]
    non_knight_frames = [BoolGridFrame(solver, height - 1, width - 1) for _ in range(n_non_knights)]
    passed = solver.int_array((height, width), -1, len(knights) + 1)
    solver.add_answer_key(passed)

    unordered_nodes = [start] + list(knights) + [end]
    nodes = solver.int_array((len(knights) + 2), 0, height * width - 1)
    solver.ensure(alldifferent(nodes))
    solver.ensure(nodes[0] == encode(start, width))
    for i in range(len(knights)):
        solver.ensure(count_true(nodes == encode(knights[i], width)) == 1)
    solver.ensure(nodes[len(knights) + 1] == encode(end, width))

    solver.ensure(passed[end] == len(knights) + 1)
    solver.add_answer_key(knight_frames)
    solver.add_answer_key(non_knight_frames)
    for y in range(height):
        for x in range(width):
            if grid[y][x] == 0:
                solver.ensure(passed[(y, x)] == 0)
            elif (y, x) in knights:
                solver.ensure(passed[(y, x)] == -1)
            else:  
                solver.ensure((passed[(y, x)] != 0) & (passed[(y, x)] != -1))
    for i in range(n_knights):
        path = knight_frames[i].active_edges_single_path()
        for s in unordered_nodes:
            encode_s = encode(s, width)
            solver.ensure(count_true(knight_frames[i].vertex_neighbors(s)) == ((encode_s == nodes[2*i + 1]) | (encode_s == nodes[2*i + 2])).cond(1, 0))
        for y in range(height):
            for x in range(width):
                if (y, x) in unordered_nodes:
                    continue
                solver.ensure((passed[y, x] == 2*i + 2) == path[y, x])
    for i in range(n_non_knights):
        path = non_knight_frames[i].active_edges_single_path()
        for s in unordered_nodes:
            encode_s = encode(s, width)
            solver.ensure(count_true(non_knight_frames[i].vertex_neighbors(s)) == ((encode_s == nodes[2*i]) | (encode_s == nodes[2*i + 1])).cond(1, 0))
        for y in range(height):
            for x in range(width):
                if (y, x) in unordered_nodes:
                    continue
                solver.ensure((passed[y, x] == 2*i + 1) == path[y, x])
    solver.ensure(passed[start] == 1)
    solver.ensure(passed[end] == len(knights) + 1)
    is_sat = solver.solve()
    return is_sat, knight_frames, non_knight_frames, passed

def _main():
    height = 6
    width = 6
    
    start = (0, 4)
    end = (5, 4)
    grid = [[1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0, 0],
            [1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1]]
    knights = [(2, 1), (3, 4), (4, 3), (4, 5)]
    is_sat, knight_frames, non_knight_frames, passed = solve_knight_tour(height, width, start, end, grid, knights)
    print(is_sat)
    if is_sat:
        print("passed:")
        print(util.stringify_array(passed, lambda x: "K" if x == -1 else "O" if x == 0 else "?" if x == None else str(x)))
        for j in range(len(non_knight_frames) + len(knight_frames)):
            if j%2 == 0:
                print("non_knight_frames[", j//2, "]: ", non_knight_frames[j//2].stringify_paths_and_loops())
            else:
                print("knight_frames[", j//2, "]: ", knight_frames[j//2].stringify_paths_and_loops())

if __name__ == "__main__":
    _main()