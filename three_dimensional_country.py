import collections.abc
import functools
from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

from cspuz.array import (
    Array1D,
    Array2D,
    BoolArray1D,
    BoolArray2D,
    IntArray1D,
    IntArray2D,
    _parse_range,
    _range_size,
)
from cspuz.expr import BoolExpr, IntExpr, Expr, Op, BoolExprLike, IntExprLike
from cspuz.graph import Graph, active_vertices_connected as _active_vertices_connected
from cspuz.solver import Solver
from cspuz import graph, count_true
from cspuz.puzzle import util

T = TypeVar("T", bound=Expr)

class Array3D(Generic[T]):
    shape: Tuple[int, int, int]
    layers: List[Array2D[T]]

    def __init__(self, layers: List[Array2D[T]]):
        self.layers = layers
        if len(layers) == 0:
            self.shape = (0, 0, 0)
        else:
            self.shape = (len(layers), layers[0].shape[0], layers[0].shape[1])

    def _getitem_impl(self, key: Any) -> Any:
        if not isinstance(key, tuple):
            z_fixed, z_start, z_stop, z_step = _parse_range(self.shape[0], key)
            if z_fixed:
                return self.layers[z_start]
            else:
                return [self.layers[i] for i in range(z_start, z_stop, z_step)]

        z_key = key[0]
        rest_key = key[1:] if len(key) > 1 else slice(None)
        if isinstance(rest_key, tuple) and len(rest_key) == 1:
            rest_key = rest_key[0]

        z_fixed, z_start, z_stop, z_step = _parse_range(self.shape[0], z_key)
        
        if z_fixed:
            return self.layers[z_start][rest_key]
        else:
            return [self.layers[i][rest_key] for i in range(z_start, z_stop, z_step)]

    def __len__(self) -> int:
        return self.shape[0]

    def __iter__(self) -> Iterator[Array2D[T]]:
        return iter(self.layers)

    @property
    def data(self) -> List[T]:
        res = []
        for layer in self.layers:
            res.extend(layer.data)
        return res

    def __bool__(self) -> bool:
        raise ValueError(
            "CSP values cannot be converted to a bool value. "
            "Perhaps you are using 'and', 'or' or 'not' on CSP values. "
            "For logical operations, use '&', '|' or '~' instead, respectively."
        )

BoolOperand3D = Union[BoolExprLike, "BoolArray3D"]
IntOperand3D = Union[IntExprLike, "IntArray3D"]

class BoolArray3D(Array3D[BoolExpr]):
    @overload
    def __init__(self, solver: Solver, shape: Tuple[int, int, int]): ...

    @overload
    def __init__(self, layers: List[BoolArray2D]): ...

    def __init__(
        self,
        arg1: Union[Solver, List[BoolArray2D]],
        shape: Optional[Tuple[int, int, int]] = None,
    ):
        if isinstance(arg1, Solver):
            if shape is None:
                raise ValueError("shape must be provided when initializing from Solver")
            depth, height, width = shape
            layers = [arg1.bool_array((height, width)) for _ in range(depth)]
        else:
            layers = arg1
        super().__init__(cast(List[Array2D[BoolExpr]], layers))

    @overload
    def __getitem__(self, key: Tuple[int, int, int]) -> BoolExpr: ...

    @overload
    def __getitem__(self, key: Union[int, Tuple[int, int, slice], Tuple[int, slice, int], Tuple[slice, int, int]]) -> BoolArray1D: ...

    @overload
    def __getitem__(self, key: Union[slice, Tuple[slice, slice, int], Tuple[slice, int, slice], Tuple[int, slice, slice]]) -> BoolArray2D: ...

    @overload
    def __getitem__(self, key: Tuple[slice, slice, slice]) -> "BoolArray3D": ...

    def __getitem__(self, key: Any) -> Union[BoolExpr, BoolArray1D, BoolArray2D, "BoolArray3D"]:
        ret = super()._getitem_impl(key)
        if isinstance(ret, (BoolExpr, BoolArray1D, BoolArray2D, BoolArray3D)):
            return ret
        if isinstance(ret, list):
            if len(ret) == 0:
                return BoolArray1D([])
            first = ret[0]
            if isinstance(first, BoolExpr):
                return BoolArray1D(ret)
            if isinstance(first, BoolArray1D):
                data = []
                for a in ret:
                    data.extend(a.data)
                return BoolArray2D(data, (len(ret), first.shape[0]))
            if isinstance(first, BoolArray2D):
                return BoolArray3D(cast(List[BoolArray2D], ret))
        return ret

    def __invert__(self) -> "BoolArray3D":
        return BoolArray3D([~l for l in self.layers])

    def __and__(self, other: BoolOperand3D) -> "BoolArray3D":
        if isinstance(other, BoolArray3D):
            return BoolArray3D([l1 & l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l & other for l in self.layers])

    def __rand__(self, other: BoolOperand3D) -> "BoolArray3D":
        return self.__and__(other)

    def __or__(self, other: BoolOperand3D) -> "BoolArray3D":
        if isinstance(other, BoolArray3D):
            return BoolArray3D([l1 | l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l | other for l in self.layers])

    def __ror__(self, other: BoolOperand3D) -> "BoolArray3D":
        return self.__or__(other)

    def __eq__(self, other: BoolOperand3D) -> "BoolArray3D": # type: ignore
        if isinstance(other, BoolArray3D):
            return BoolArray3D([l1 == l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l == other for l in self.layers])

    def __ne__(self, other: BoolOperand3D) -> "BoolArray3D": # type: ignore
        if isinstance(other, BoolArray3D):
            return BoolArray3D([l1 != l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l != other for l in self.layers])

    def __xor__(self, other: BoolOperand3D) -> "BoolArray3D":
        return self.__ne__(other)

    def __rxor__(self, other: BoolOperand3D) -> "BoolArray3D":
        return self.__xor__(other)

    def cond(self, t: IntOperand3D, f: IntOperand3D) -> "IntArray3D":
        if isinstance(t, IntArray3D) and isinstance(f, IntArray3D):
            return IntArray3D([l.cond(t_l, f_l) for l, t_l, f_l in zip(self.layers, t.layers, f.layers)])
        elif isinstance(t, IntArray3D):
            return IntArray3D([l.cond(t_l, f) for l, t_l in zip(self.layers, t.layers)])
        elif isinstance(f, IntArray3D):
            return IntArray3D([l.cond(t, f_l) for l, f_l in zip(self.layers, f.layers)])
        else:
            return IntArray3D([l.cond(t, f) for l in self.layers])

    def then(self, other: BoolOperand3D) -> "BoolArray3D":
        if isinstance(other, BoolArray3D):
            return BoolArray3D([l1.then(l2) for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l.then(other) for l in self.layers])

    def fold_or(self) -> BoolExpr:
        return BoolExpr(Op.OR, self.data)

    def fold_and(self) -> BoolExpr:
        return BoolExpr(Op.AND, self.data)

    def flatten(self) -> BoolArray1D:
        return BoolArray1D(self.data)

    def count_true(self) -> IntExpr:
        import cspuz.constraints
        return cspuz.constraints.count_true(self.data)

    def six_neighbor_indices(self, z: Union[int, Tuple[int, int, int]], y: Optional[int] = None, x: Optional[int] = None) -> List[Tuple[int, int, int]]:
        if x is None:
            z_coord, y_coord, x_coord = cast(Tuple[int, int, int], z)
        else:
            z_coord = cast(int, z)
            y_coord = cast(int, y)
            x_coord = cast(int, x)
        
        ret = []
        depth, height, width = self.shape
        if z_coord > 0: ret.append((z_coord - 1, y_coord, x_coord))
        if z_coord < depth - 1: ret.append((z_coord + 1, y_coord, x_coord))
        if y_coord > 0: ret.append((z_coord, y_coord - 1, x_coord))
        if y_coord < height - 1: ret.append((z_coord, y_coord + 1, x_coord))
        if x_coord > 0: ret.append((z_coord, y_coord, x_coord - 1))
        if x_coord < width - 1: ret.append((z_coord, y_coord, x_coord + 1))
        return ret

    def six_neighbors(self, z: Union[int, Tuple[int, int, int]], y: Optional[int] = None, x: Optional[int] = None) -> BoolArray1D:
        indices = self.six_neighbor_indices(z, y, x)
        return BoolArray1D([self[i] for i in indices])

class IntArray3D(Array3D[IntExpr]):
    @overload
    def __init__(self, solver: Solver, shape: Tuple[int, int, int], min_val: int, max_val: int): ...

    @overload
    def __init__(self, layers: List[IntArray2D]): ...

    def __init__(
        self,
        arg1: Union[Solver, List[IntArray2D]],
        shape: Optional[Tuple[int, int, int]] = None,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
    ):
        if isinstance(arg1, Solver):
            if shape is None or min_val is None or max_val is None:
                raise ValueError(
                    "shape, min_val, and max_val must be provided when initializing from Solver"
                )
            depth, height, width = shape
            layers = [arg1.int_array((height, width), min_val, max_val) for _ in range(depth)]
        else:
            layers = arg1
        super().__init__(cast(List[Array2D[IntExpr]], layers))

    def __getitem__(self, key: Any) -> Union[IntExpr, IntArray1D, IntArray2D, "IntArray3D"]:
        ret = super()._getitem_impl(key)
        if isinstance(ret, (IntExpr, IntArray1D, IntArray2D, IntArray3D)):
            return ret
        if isinstance(ret, list):
            if len(ret) == 0:
                return IntArray1D([])
            first = ret[0]
            if isinstance(first, IntExpr):
                return IntArray1D(ret)
            if isinstance(first, IntArray1D):
                data = []
                for a in ret:
                    data.extend(a.data)
                return IntArray2D(data, (len(ret), first.shape[0]))
            if isinstance(first, IntArray2D):
                return IntArray3D(cast(List[IntArray2D], ret))
        return ret

    def __neg__(self) -> "IntArray3D":
        return IntArray3D([-l for l in self.layers])

    def __add__(self, other: IntOperand3D) -> "IntArray3D":
        if isinstance(other, IntArray3D):
            return IntArray3D([l1 + l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return IntArray3D([l + other for l in self.layers])

    def __radd__(self, other: IntOperand3D) -> "IntArray3D":
        return self.__add__(other)

    def __sub__(self, other: IntOperand3D) -> "IntArray3D":
        if isinstance(other, IntArray3D):
            return IntArray3D([l1 - l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return IntArray3D([l - other for l in self.layers])

    def __rsub__(self, other: IntOperand3D) -> "IntArray3D":
        if isinstance(other, IntArray3D):
            return IntArray3D([l2 - l1 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return IntArray3D([other - l for l in self.layers])

    def __eq__(self, other: IntOperand3D) -> "BoolArray3D": # type: ignore
        if isinstance(other, IntArray3D):
            return BoolArray3D([l1 == l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l == other for l in self.layers])

    def __ne__(self, other: IntOperand3D) -> "BoolArray3D": # type: ignore
        if isinstance(other, IntArray3D):
            return BoolArray3D([l1 != l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l != other for l in self.layers])

    def __ge__(self, other: IntOperand3D) -> "BoolArray3D":
        if isinstance(other, IntArray3D):
            return BoolArray3D([l1 >= l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l >= other for l in self.layers])

    def __gt__(self, other: IntOperand3D) -> "BoolArray3D":
        if isinstance(other, IntArray3D):
            return BoolArray3D([l1 > l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l > other for l in self.layers])

    def __le__(self, other: IntOperand3D) -> "BoolArray3D":
        if isinstance(other, IntArray3D):
            return BoolArray3D([l1 <= l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l <= other for l in self.layers])

    def __lt__(self, other: IntOperand3D) -> "BoolArray3D":
        if isinstance(other, IntArray3D):
            return BoolArray3D([l1 < l2 for l1, l2 in zip(self.layers, other.layers)])
        else:
            return BoolArray3D([l < other for l in self.layers])

    def flatten(self) -> IntArray1D:
        return IntArray1D(self.data)

    def alldifferent(self) -> BoolExpr:
        return BoolExpr(Op.ALLDIFF, self.data)

    def six_neighbor_indices(self, z: Union[int, Tuple[int, int, int]], y: Optional[int] = None, x: Optional[int] = None) -> List[Tuple[int, int, int]]:
        if x is None:
            z_coord, y_coord, x_coord = cast(Tuple[int, int, int], z)
        else:
            z_coord = cast(int, z)
            y_coord = cast(int, y)
            x_coord = cast(int, x)
        
        ret = []
        depth, height, width = self.shape
        if z_coord > 0: ret.append((z_coord - 1, y_coord, x_coord))
        if z_coord < depth - 1: ret.append((z_coord + 1, y_coord, x_coord))
        if y_coord > 0: ret.append((z_coord, y_coord - 1, x_coord))
        if y_coord < height - 1: ret.append((z_coord, y_coord + 1, x_coord))
        if x_coord > 0: ret.append((z_coord, y_coord, x_coord - 1))
        if x_coord < width - 1: ret.append((z_coord, y_coord, x_coord + 1))
        return ret

    def six_neighbors(self, z: Union[int, Tuple[int, int, int]], y: Optional[int] = None, x: Optional[int] = None) -> IntArray1D:
        indices = self.six_neighbor_indices(z, y, x)
        return IntArray1D([self[i] for i in indices])

def stringify_array_3d(array: Union[BoolArray3D, IntArray3D], symbol_map=None) -> str:
    res = []
    for i, layer in enumerate(array.layers):
        res.append(f"layer {i + 1}:")
        res.append(util.stringify_array(layer, symbol_map))
    return "\n".join(res)

def _grid_graph_3d(depth: int, height: int, width: int) -> Graph:
    graph = Graph(depth * height * width)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                v = (z * height + y) * width + x
                if x < width - 1:
                    graph.add_edge(v, v + 1)
                if y < height - 1:
                    graph.add_edge(v, v + width)
                if z < depth - 1:
                    graph.add_edge(v, v + height * width)
    return graph

def active_vertices_connected(
    solver: Solver,
    is_active: BoolArray3D,
    *,
    acyclic: bool = False,
    use_graph_primitive: Optional[bool] = None,
) -> None:
    depth, height, width = is_active.shape
    graph = _grid_graph_3d(depth, height, width)
    _active_vertices_connected(
        solver, is_active.data, graph, acyclic=acyclic, use_graph_primitive=use_graph_primitive
    )

'''
universal rules:
the tiles are colored either white (True) or black (False)
the white tiles are connected by surfaces
the black tiles cannot be adjacent in surfaces
'''

'''
specific rules for kurodoko: 
the tiles with nonzero numbers in grid must be white (True)
the tiles with zero numbers in grid must be black (False)
the nonzero numbers in grid must be the number of white tiles seen from the tile in direction of plus and minus x, y, z axes (including the tile itself)
'''
def solve_kurodoko(depth, height, width, grid):
    solver = Solver()
    is_white = BoolArray3D(solver, (depth, height, width))
    solver.add_answer_key(is_white)

    active_vertices_connected(solver, is_white)

    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if grid[z][y][x] != 0:
                    solver.ensure(is_white[z][y][x])
    
    solver.ensure(is_white[1:, :, :] | is_white[:-1, :, :])
    solver.ensure(is_white[:, 1:, :] | is_white[:, :-1, :])
    solver.ensure(is_white[:, :, 1:] | is_white[:, :, :-1])

    to_left = IntArray3D(solver, (depth, height, width), 0, width)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if x > 0:
                    solver.ensure(to_left[z][y][x] == (is_white[z][y][x]).cond(to_left[z][y][x - 1] + 1, 0))
                else:
                    solver.ensure(to_left[z][y][x] == (is_white[z][y][x]).cond(1, 0))

    to_right = IntArray3D(solver, (depth, height, width), 0, width)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if x < width - 1:
                    solver.ensure(to_right[z][y][x] == (is_white[z][y][x]).cond(to_right[z][y][x + 1] + 1, 0))
                else:
                    solver.ensure(to_right[z][y][x] == (is_white[z][y][x]).cond(1, 0))

    to_up = IntArray3D(solver, (depth, height, width), 0, height)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if y > 0:
                    solver.ensure(to_up[z][y][x] == (is_white[z][y][x]).cond(to_up[z][y - 1][x] + 1, 0))
                else:
                    solver.ensure(to_up[z][y][x] == (is_white[z][y][x]).cond(1, 0))

    to_down = IntArray3D(solver, (depth, height, width), 0, height)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if y < height - 1:
                    solver.ensure(to_down[z][y][x] == (is_white[z][y][x]).cond(to_down[z][y + 1][x] + 1, 0))
                else:
                    solver.ensure(to_down[z][y][x] == (is_white[z][y][x]).cond(1, 0))
    
    to_front = IntArray3D(solver, (depth, height, width), 0, depth)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if z > 0:
                    solver.ensure(to_front[z][y][x] == (is_white[z][y][x]).cond(to_front[z - 1][y][x] + 1, 0))
                else:
                    solver.ensure(to_front[z][y][x] == (is_white[z][y][x]).cond(1, 0))

    to_back = IntArray3D(solver, (depth, height, width), 0, depth)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if z < depth - 1:
                    solver.ensure(to_back[z][y][x] == (is_white[z][y][x]).cond(to_back[z + 1][y][x] + 1, 0))
                else:
                    solver.ensure(to_back[z][y][x] == (is_white[z][y][x]).cond(1, 0))
    
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if grid[z][y][x] != 0:
                    solver.ensure(to_left[z][y][x] + to_right[z][y][x] + to_up[z][y][x] + to_down[z][y][x] + to_front[z][y][x] + to_back[z][y][x] == grid[z][y][x] + 5)

    is_sat = solver.solve()
    return is_sat, is_white

'''
specific rules for hitori: 
the white tiles on the same line (x, y, z axes) must have different numbers in grid
'''
def solve_hitori(depth, height, width, grid):
    solver = Solver()
    is_white = BoolArray3D(solver, (depth, height, width))
    solver.add_answer_key(is_white)

    active_vertices_connected(solver, is_white)
    
    solver.ensure(is_white[1:, :, :] | is_white[:-1, :, :])
    solver.ensure(is_white[:, 1:, :] | is_white[:, :-1, :])
    solver.ensure(is_white[:, :, 1:] | is_white[:, :, :-1])

    for z in range(depth):
        for y in range(height):
            number_list = [grid[z][y][x] for x in range(width)]
            numbers = {_ for _ in number_list if number_list.count(_) > 1}
            for n in numbers:
                solver.ensure(count_true([is_white[z][y][x] & (grid[z][y][x] == n) for x in range(width)]) <= 1)
    
    for z in range(depth):
        for x in range(width):
            number_list = [grid[z][y][x] for y in range(height)]
            numbers = {_ for _ in number_list if number_list.count(_) > 1}
            for n in numbers:
                solver.ensure(count_true([is_white[z][y][x] & (grid[z][y][x] == n) for y in range(height)]) <= 1)
    
    for y in range(height):
        for x in range(width):
            number_list = [grid[z][y][x] for z in range(depth)]
            numbers = {_ for _ in number_list if number_list.count(_) > 1}
            for n in numbers:
                solver.ensure(count_true([is_white[z][y][x] & (grid[z][y][x] == n) for z in range(depth)]) <= 1)

    is_sat = solver.solve()
    return is_sat, is_white

'''
specific rules for kurochute: 
the tiles with nonzero numbers in grid must be white (True)
for each tile with nonzero number in grid, there must exist and only exist one black tile which is in the same line (x, y, z axes) with the tile and has the distance from the tile equal to the number
'''
def solve_kurochute(depth, height, width, grid):
    solver = Solver()
    is_white = BoolArray3D(solver, (depth, height, width))
    solver.add_answer_key(is_white)
    
    active_vertices_connected(solver, is_white)

    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if grid[z][y][x] != 0:
                    solver.ensure(is_white[z][y][x])
    
    solver.ensure(is_white[1:, :, :] | is_white[:-1, :, :])
    solver.ensure(is_white[:, 1:, :] | is_white[:, :-1, :])
    solver.ensure(is_white[:, :, 1:] | is_white[:, :, :-1])

    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if grid[z][y][x] != 0:
                    ds = grid[z][y][x]
                    tiles = []
                    if x - ds >= 0:
                        tiles.append(~is_white[z][y][x - ds])
                    if x + ds < width:
                        tiles.append(~is_white[z][y][x + ds])
                    if y - ds >= 0:
                        tiles.append(~is_white[z][y - ds][x])
                    if y + ds < height:
                        tiles.append(~is_white[z][y + ds][x])
                    if z - ds >= 0:
                        tiles.append(~is_white[z - ds][y][x])
                    if z + ds < depth:
                        tiles.append(~is_white[z + ds][y][x])
                    solver.ensure(count_true(tiles) == 1)

    is_sat = solver.solve()
    return is_sat, is_white

'''
specific rules for yajisan-kazusan:
the white colored clues (nonzero numbers) represent the number of black tiles seen from the tile in the specific direction
the black colored clues (nonzero numbers) does not have any information
'''
def solve_yajisan(depth, height, width, grid):
    solver = Solver()
    is_white = BoolArray3D(solver, (depth, height, width))
    solver.add_answer_key(is_white)
    
    active_vertices_connected(solver, is_white)

    solver.ensure(is_white[1:, :, :] | is_white[:-1, :, :])
    solver.ensure(is_white[:, 1:, :] | is_white[:, :-1, :])
    solver.ensure(is_white[:, :, 1:] | is_white[:, :, :-1])

    to_left = IntArray3D(solver, (depth, height, width), 0, width)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if x > 0:
                    solver.ensure(to_left[z][y][x] == to_left[z][y][x - 1] + (is_white[z][y][x]).cond(0, 1))
                else:
                    solver.ensure(to_left[z][y][x] == (is_white[z][y][x]).cond(0, 1))

    to_right = IntArray3D(solver, (depth, height, width), 0, width)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if x < width - 1:
                    solver.ensure(to_right[z][y][x] == to_right[z][y][x + 1] + (is_white[z][y][x]).cond(0, 1))
                else:
                    solver.ensure(to_right[z][y][x] == (is_white[z][y][x]).cond(0, 1))

    to_up = IntArray3D(solver, (depth, height, width), 0, height)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if y > 0:
                    solver.ensure(to_up[z][y][x] == to_up[z][y - 1][x] + (is_white[z][y][x]).cond(0, 1))
                else:
                    solver.ensure(to_up[z][y][x] == (is_white[z][y][x]).cond(0, 1))

    to_down = IntArray3D(solver, (depth, height, width), 0, height)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if y < height - 1:
                    solver.ensure(to_down[z][y][x] == to_down[z][y + 1][x] + (is_white[z][y][x]).cond(0, 1))
                else:
                    solver.ensure(to_down[z][y][x] == (is_white[z][y][x]).cond(0, 1))

    to_front = IntArray3D(solver, (depth, height, width), 0, depth)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if z > 0:
                    solver.ensure(to_front[z][y][x] == to_front[z - 1][y][x] + (is_white[z][y][x]).cond(0, 1))
                else:
                    solver.ensure(to_front[z][y][x] == (is_white[z][y][x]).cond(0, 1))

    to_back = IntArray3D(solver, (depth, height, width), 0, depth)
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if z < depth - 1:
                    solver.ensure(to_back[z][y][x] == to_back[z + 1][y][x] + (is_white[z][y][x]).cond(0, 1))
                else:
                    solver.ensure(to_back[z][y][x] == (is_white[z][y][x]).cond(0, 1))
    

    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if grid[z][y][x] != 0:
                    if grid[z][y][x][1] == 0:
                        solver.ensure((~is_white[z][y][x]) | (to_left[z][y][x] == grid[z][y][x][0]))
                    elif grid[z][y][x][1] == 1:
                        solver.ensure((~is_white[z][y][x]) | (to_right[z][y][x] == grid[z][y][x][0]))
                    elif grid[z][y][x][1] == 2:
                        solver.ensure((~is_white[z][y][x]) | (to_up[z][y][x] == grid[z][y][x][0]))
                    elif grid[z][y][x][1] == 3:
                        solver.ensure((~is_white[z][y][x]) | (to_down[z][y][x] == grid[z][y][x][0]))
                    elif grid[z][y][x][1] == 4:
                        solver.ensure((~is_white[z][y][x]) | (to_front[z][y][x] == grid[z][y][x][0]))
                    elif grid[z][y][x][1] == 5:
                        solver.ensure((~is_white[z][y][x]) | (to_back[z][y][x] == grid[z][y][x][0]))

    is_sat = solver.solve()
    return is_sat, is_white

'''
specific rules for context:
the black clues (nonnegative numbers) represent the number of black tiles that has a common node but no common edge or surface with the tile with the clue
the white clues (nonnegative numbers) represent the number of black tiles that has a common surface with the tile with the clue
'''
def solve_context(depth, height, width, grid):
    solver = Solver()
    is_white = BoolArray3D(solver, (depth, height, width))
    solver.add_answer_key(is_white)

    active_vertices_connected(solver, is_white)

    solver.ensure(is_white[1:, :, :] | is_white[:-1, :, :])
    solver.ensure(is_white[:, 1:, :] | is_white[:, :-1, :])
    solver.ensure(is_white[:, :, 1:] | is_white[:, :, :-1])

    for z in range(depth):
        for y in range(height):
            for x in range(width):
                if grid[z][y][x] != -1:
                    tiles_diag = []
                    if x > 0 and y > 0 and z > 0:
                        tiles_diag.append(~is_white[z - 1][y - 1][x - 1])
                    if x > 0 and y > 0 and z < depth - 1:
                        tiles_diag.append(~is_white[z + 1][y - 1][x - 1])
                    if x > 0 and y < height - 1 and z > 0:
                        tiles_diag.append(~is_white[z - 1][y + 1][x - 1])
                    if x > 0 and y < height - 1 and z < depth - 1:
                        tiles_diag.append(~is_white[z + 1][y + 1][x - 1])
                    if x < width - 1 and y > 0 and z > 0:
                        tiles_diag.append(~is_white[z - 1][y - 1][x + 1])
                    if x < width - 1 and y > 0 and z < depth - 1:
                        tiles_diag.append(~is_white[z + 1][y - 1][x + 1])
                    if x < width - 1 and y < height - 1 and z > 0:
                        tiles_diag.append(~is_white[z - 1][y + 1][x + 1])
                    if x < width - 1 and y < height - 1 and z < depth - 1:
                        tiles_diag.append(~is_white[z + 1][y + 1][x + 1])
                    tiles_surface = []
                    if x > 0:
                        tiles_surface.append(~is_white[z][y][x - 1])
                    if x < width - 1:
                        tiles_surface.append(~is_white[z][y][x + 1])
                    if y > 0:
                        tiles_surface.append(~is_white[z][y - 1][x])
                    if y < height - 1:
                        tiles_surface.append(~is_white[z][y + 1][x])
                    if z > 0:
                        tiles_surface.append(~is_white[z - 1][y][x])
                    if z < depth - 1:
                        tiles_surface.append(~is_white[z + 1][y][x])
                    solver.ensure(((~is_white[z][y][x]) & (count_true(tiles_diag) == grid[z][y][x])) | ((is_white[z][y][x]) & (count_true(tiles_surface) == grid[z][y][x])))

    is_sat = solver.solve()
    return is_sat, is_white


def _main():

    depth, height, width = 5, 5, 5
    grid = [[[0, 0, 0, 0, 0], [2, 0, 0, 0, 2], [0, 3, 0, 3, 0], [0, 0, 0, 0, 0], [0, 0, 2, 0, 0]],
    [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
    [[0, 0, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
    [[3, 0, 0, 0, 3], [0, 0, 0, 0, 0], [2, 0, 0, 0, 0], [0, 0, 0, 0, 0], [2, 0, 0, 0, 3]],
    [[0, 0, 0, 0, 0], [0, 0, 0, 3, 0], [0, 0, 0, 0, 0], [0, 0, 0, 3, 0], [0, 0, 0, 0, 0]]]
    is_sat, is_white = solve_kurodoko(depth, height, width, grid)
    print("kurodoko:", is_sat)
    if is_sat:
        print(stringify_array_3d(is_white, lambda x: "." if x else "?" if x is None else "B"))
    
    depth, height, width = 5, 5, 5
    grid = [[[0, 1, 3, 0, 4], [5, 2, 3, 8, 5], [2, 6, 4, 5, 4], [3, 4, 6, 6, 8], [4, 4, 6, 7, 9]],
    [[9, 2, 3, 4, 5], [2, 9, 4, 9, 9], [4, 1, 8, 3, 7], [4, 5, 6, 7, 8], [8, 6, 4, 8, 9]],
    [[2, 3, 4, 5, 1], [3, 1, 5, 7, 7], [4, 5, 6, 2, 7], [4, 6, 9, 8, 9], [3, 7, 7, 9, 0]],
    [[4, 4, 5, 6, 5], [4, 5, 6, 7, 8], [2, 6, 6, 8, 4], [6, 6, 8, 1, 7], [7, 8, 9, 1, 5]],
    [[4, 5, 3, 7, 8], [5, 7, 7, 8, 9], [6, 2, 8, 9, 6], [0, 8, 8, 0, 7], [8, 0, 0, 1, 1]]]
    is_sat, is_white = solve_hitori(depth, height, width, grid)
    print("hitori:", is_sat)
    if is_sat:
        print(stringify_array_3d(is_white, lambda x: "." if x else "?" if x is None else "B"))
    
    depth, height, width = 5, 5, 5
    grid = [[[0, 0, 2, 0, 0], [0, 0, 0, 0, 0], [0, 1, 0, 0, 3], [0, 0, 0, 2, 0], [2, 0, 1, 0, 0]],
    [[0, 0, 2, 2, 0], [2, 0, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 3], [0, 0, 1, 1, 0]],
    [[0, 3, 1, 0, 0], [0, 0, 0, 0, 0], [1, 0, 0, 0, 2], [0, 0, 0, 0, 2], [0, 0, 0, 0, 0]],
    [[1, 0, 2, 3, 0], [3, 0, 0, 3, 3], [0, 0, 1, 3, 0], [0, 0, 0, 0, 0], [0, 0, 1, 2, 0]],
    [[0, 0, 0, 0, 2], [0, 1, 0, 0, 3], [2, 0, 1, 1, 0], [0, 0, 3, 0, 0], [0, 0, 2, 0, 0]]]
    is_sat, is_white = solve_kurochute(depth, height, width, grid)
    print("kurochute:", is_sat)
    if is_sat:
        print(stringify_array_3d(is_white, lambda x: "." if x else "?" if x is None else "B"))
    
    depth, height, width = 5, 5, 5
    grid = [[[0, (0, 1), 0, 0, (2, 3)], [0, 0, 0, 0, 0], [(1, 2), 0, 0, 0, 0], [(1, 3), 0, 0, 0, (2, 0)], [(1, 2), 0, 0, (2, 2), 0]],
    [[0, (1, 1), 0, 0, 0], [(0, 1), 0, 0, 0, 0], [0, 0, 0, (1, 2), (1, 2)], [(2, 2), (0, 0), 0, 0, 0], [0, 0, (1, 0), 0, (1, 5)]],
    [[0, 0, 0, 0, 0], [(1, 5), (0, 1), 0, 0, 0], [0, 0, 0, (1, 0), 0], [0, 0, 0, 0, (2, 0)], [0, 0, 0, (0, 4), (2, 0)]],
    [[0, 0, 0, 0, (1, 0)], [0, (0, 0), (1, 4), 0, 0], [(1, 1), 0, 0, 0, 0], [0, (1, 5), 0, (2, 0), (1, 5)], [(1, 5), (2, 4), 0, 0, 0]],
    [[0, (1, 4), 0, 0, 0], [0, (1, 2), 0, 0, (1, 4)], [0, 0, 0, 0, (0, 2)], [(1, 2), 0, (1, 1), 0, 0], [0, (1, 4), (2, 2), 0, (2, 2)]]]
    is_sat, is_white = solve_yajisan(depth, height, width, grid)
    print("yajisan:", is_sat)
    if is_sat:
        print(stringify_array_3d(is_white, lambda x: "." if x else "?" if x is None else "B"))

    depth, height, width = 5, 5, 5
    grid = [[[-1, 2, -1, 1, -1], [-1, -1, -1, -1, 2], [-1, 1, -1, -1, -1], [2, -1, -1, -1, 0], [-1, -1, 2, -1, -1]],
    [[-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, 4, -1], [-1, -1, -1, -1, -1], [2, -1, -1, -1, -1]],
    [[-1, -1, -1, -1, -1], [-1, -1, -1, -1, 0], [-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, 3, -1, 2]], 
    [[-1, -1, -1, -1, -1], [-1, -1, -1, -1, 1], [-1, 7, -1, 2, -1], [3, -1, -1, -1, -1], [-1, -1, -1, 3, -1]],
    [[-1, -1, -1, -1, -1], [-1, -1, 2, 3, -1], [-1, -1, -1, -1, 0], [-1, -1, 0, -1, -1], [-1, -1, -1, -1, 1]]]
    is_sat, is_white = solve_context(depth, height, width, grid)
    print("context:", is_sat)
    if is_sat:
        print(stringify_array_3d(is_white, lambda x: "." if x else "?" if x is None else "B"))

if __name__ == "__main__":
    _main()