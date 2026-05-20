import itertools
from typing import Iterator, Optional, Tuple, Union

from .array import BoolArray1D, BoolArray2D
from .expr import BoolExpr
from .solver import Solver


class BoolGridFrame:
    """
    Frame of `height` * `width` grid, each of whose edges is associated with
    a bool variable.
    """

    def __init__(
        self,
        solver: Solver,
        height: int,
        width: int,
        horizontal: Optional[BoolArray2D] = None,
        vertical: Optional[BoolArray2D] = None,
    ):
        self.solver = solver
        self.height = height
        self.width = width

        if horizontal is None:
            self.horizontal = solver.bool_array((height + 1, width))
        else:
            self.horizontal = horizontal

        if vertical is None:
            self.vertical = solver.bool_array((height, width + 1))
        else:
            self.vertical = vertical

    def __getitem__(self, item: Tuple[int, int]) -> BoolExpr:
        y, x = item
        if not (0 <= y <= self.height * 2 and 0 <= x <= self.width * 2):
            raise IndexError("index out of range")
        if y % 2 == 0 and x % 2 == 1:
            return self.horizontal[y // 2, x // 2]
        elif y % 2 == 1 and x % 2 == 0:
            return self.vertical[y // 2, x // 2]
        else:
            raise IndexError("index does not specify a loop edge")

    def all_edges(self) -> BoolArray1D:
        return BoolArray1D(list(itertools.chain(self.horizontal, self.vertical)))

    def __iter__(self) -> Iterator[BoolExpr]:
        return itertools.chain(self.horizontal, self.vertical)

    def cell_neighbors(
        self, y: Union[int, Tuple[int, int]], x: Optional[int] = None
    ) -> BoolArray1D:
        if x is None:
            if isinstance(y, int):
                raise TypeError("two integers must be provided to 'cell_neighbors'")
            y2, x2 = y
        else:
            if x is None or isinstance(y, tuple):
                raise TypeError("two integers must be provided to 'cell_neighbors'")
            y2 = y
            x2 = x
        if not (0 <= y2 < self.height and 0 <= x2 < self.width):
            raise IndexError("index out of range")
        return BoolArray1D(
            [
                self.horizontal[y2, x2],
                self.horizontal[y2 + 1, x2],
                self.vertical[y2, x2],
                self.vertical[y2, x2 + 1],
            ]
        )

    def vertex_neighbors(
        self, y: Union[int, Tuple[int, int]], x: Optional[int] = None
    ) -> BoolArray1D:
        if x is None:
            if isinstance(y, int):
                raise TypeError("two integers must be provided to 'vertex_neighbors'")
            y2, x2 = y
        else:
            if x is None or isinstance(y, tuple):
                raise TypeError("two integers must be provided to 'vertex_neighbors'")
            y2 = y
            x2 = x
        if not (0 <= y2 <= self.height and 0 <= x2 <= self.width):
            raise IndexError("index out of range")

        res = []
        if y2 > 0:
            res.append(self.vertical[y2 - 1, x2])
        if y2 < self.height:
            res.append(self.vertical[y2, x2])
        if x2 > 0:
            res.append(self.horizontal[y2, x2 - 1])
        if x2 < self.width:
            res.append(self.horizontal[y2, x2])
        return BoolArray1D(res)

    def dual(self) -> "BoolInnerGridFrame":
        return BoolInnerGridFrame(
            solver=self.solver,
            height=self.height + 1,
            width=self.width + 1,
            horizontal=self.vertical,
            vertical=self.horizontal,
        )

    def single_loop(self) -> BoolArray2D:
        from . import graph

        return graph.active_edges_single_cycle(self.solver, self)

    def active_edges_single_path(self) -> BoolArray2D:
        from . import graph

        return graph.active_edges_single_path(self.solver, self)

    def stringify_vertex_adjacencies(self) -> str:
        """
        List each intersection and the status of edges connected to it.
        Format: (y, x): (y1, x1)[status] (y2, x2)[status] ...
        Status: 'V' for True, 'X' for False, ' ' for None.
        """
        res = []
        for y in range(self.height + 1):
            for x in range(self.width + 1):
                line = [f"({y}, {x}):"]
                # Up
                if y > 0:
                    sol = self.vertical[y - 1, x].sol
                    line.append(f"({y-1}, {x}){'V' if sol is True else ('X' if sol is False else ' ')}")
                # Down
                if y < self.height:
                    sol = self.vertical[y, x].sol
                    line.append(f"({y+1}, {x}){'V' if sol is True else ('X' if sol is False else ' ')}")
                # Left
                if x > 0:
                    sol = self.horizontal[y, x - 1].sol
                    line.append(f"({y}, {x-1}){'V' if sol is True else ('X' if sol is False else ' ')}")
                # Right
                if x < self.width:
                    sol = self.horizontal[y, x].sol
                    line.append(f"({y}, {x+1}){'V' if sol is True else ('X' if sol is False else ' ')}")
                res.append(" ".join(line))
        return "\n".join(res)

    def stringify_paths_and_loops(self) -> str:
        """
        Find and represent all paths and loops formed by active edges on the grid.
        Only works if there are no branches (degree <= 2 for all intersections).
        """
        adj = {}
        for y in range(self.height + 1):
            for x in range(self.width + 1):
                neighbors = []
                if x < self.width and self.horizontal[y, x].sol is True:
                    neighbors.append((y, x + 1))
                if x > 0 and self.horizontal[y, x - 1].sol is True:
                    neighbors.append((y, x - 1))
                if y < self.height and self.vertical[y, x].sol is True:
                    neighbors.append((y + 1, x))
                if y > 0 and self.vertical[y - 1, x].sol is True:
                    neighbors.append((y - 1, x))
                
                if neighbors:
                    if len(neighbors) > 2:
                        return "Grid contains branches (degree > 2). Cannot represent as simple paths/loops."
                    adj[(y, x)] = neighbors

        visited = set()
        results = []

        # Find paths (start from vertices with degree 1)
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

        # Find loops (remaining active vertices must have degree 2)
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


class BoolInnerGridFrame:
    def __init__(
        self,
        solver: Solver,
        height: int,
        width: int,
        horizontal: Optional[BoolArray2D] = None,
        vertical: Optional[BoolArray2D] = None,
    ) -> None:
        self.solver = solver
        self.height = height
        self.width = width

        if horizontal is None:
            self.horizontal = solver.bool_array((height - 1, width))
        else:
            self.horizontal = horizontal

        if vertical is None:
            self.vertical = solver.bool_array((height, width - 1))
        else:
            self.vertical = vertical

    def dual(self) -> BoolGridFrame:
        return BoolGridFrame(
            solver=self.solver,
            height=self.height - 1,
            width=self.width - 1,
            horizontal=self.vertical,
            vertical=self.horizontal,
        )

    def __iter__(self) -> Iterator[BoolExpr]:
        return iter(self.dual())
