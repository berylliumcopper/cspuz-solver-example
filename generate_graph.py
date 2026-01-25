from cspuz import graph
from cspuz.graph import Graph
from cspuz.array import BoolArray1D

class BoolFrame:
    """
    A frame representing an arbitrary graph, where each edge is associated with a boolean variable.
    """
    def __init__(self, solver, v, e):
        self.solver = solver
        self.vertices = v
        self.edges_input = e
        
        # Mapping from user vertex ID to internal 0-indexed integer
        self.v_map = {vid: i for i, vid in enumerate(v)}
        self.num_vertices = len(v)
        
        self.graph = Graph(self.num_vertices)
        for u, v_edge in e:
            self.graph.add_edge(self.v_map[u], self.v_map[v_edge])
        
        # Create boolean variables for each edge
        self.edge_vars = solver.bool_array(len(e))

    def __iter__(self):
        """
        Iterate over the boolean variables associated with the edges.
        This allows things like solver.add_answer_key(bool_frame) to work.
        """
        return iter(self.edge_vars)

    def active_edges_single_cycle(self):
        """
        Add a constraint that the active edges form a single cycle.
        Returns a BoolArray1D representing whether each vertex is passed by the cycle.
        """
        return graph.active_edges_single_cycle(self.solver, self.edge_vars, self.graph)

    def stringify_vertex_adjacencies(self):
        """
        List each vertex and the status of edges connected to it.
        Format: VertexID: Neighbor1[status] Neighbor2[status] ...
        Status: 'V' for True, 'X' for False, ' ' for None.
        """
        res = []
        for i, vid in enumerate(self.vertices):
            line = [f"{vid}:"]
            for neighbor_idx, edge_id in self.graph.incident_edges[i]:
                neighbor_vid = self.vertices[neighbor_idx]
                sol = self.edge_vars[edge_id].sol
                status = 'V' if sol is True else ('X' if sol is False else ' ')
                line.append(f"{neighbor_vid}{status}")
            res.append(" ".join(line))
        return "\n".join(res)

    def stringify_paths_and_loops(self):
        """
        Find and represent all paths and loops formed by active edges.
        Only works if there are no branches (degree <= 2 for all active vertices).
        """
        # Build adjacency list for active edges
        adj = [[] for _ in range(self.num_vertices)]
        for i, (u_idx, v_idx) in enumerate(self.graph.edges):
            if self.edge_vars[i].sol is True:
                adj[u_idx].append(v_idx)
                adj[v_idx].append(u_idx)
        
        for i in range(self.num_vertices):
            if len(adj[i]) > 2:
                return "Graph contains branches (degree > 2). Cannot represent as simple paths/loops."

        visited = [False] * self.num_vertices
        results = []

        # Find paths (start from vertices with degree 1)
        for i in range(self.num_vertices):
            if not visited[i] and len(adj[i]) == 1:
                path = []
                curr = i
                while curr is not None:
                    visited[curr] = True
                    path.append(str(self.vertices[curr]))
                    next_node = None
                    for neighbor in adj[curr]:
                        if not visited[neighbor]:
                            next_node = neighbor
                            break
                    curr = next_node
                results.append("path: " + " ".join(path))

        # Find loops (remaining active vertices must have degree 2)
        for i in range(self.num_vertices):
            if not visited[i] and len(adj[i]) == 2:
                loop = []
                curr = i
                while not visited[curr]:
                    visited[curr] = True
                    loop.append(str(self.vertices[curr]))
                    # For a loop, there must be a neighbor that isn't the previous one
                    # We use visited to track, but for the very first step we need to pick one neighbor
                    next_node = None
                    for neighbor in adj[curr]:
                        if not visited[neighbor]:
                            next_node = neighbor
                            break
                    if next_node is None: # Loop closed
                        break
                    curr = next_node
                results.append("loop: " + " ".join(loop))

        return "\n".join(results)

def generate_graph(solver, v, e):
    """
    Returns a BoolFrame object that describes the graph.
    
    :param solver: The cspuz Solver object.
    :param v: list of non-repeat integers, describing the vertices.
    :param e: list of tuples, each tuple having two integers (u, v), meaning an edge.
    :return: A BoolFrame object.
    """
    return BoolFrame(solver, v, e)
