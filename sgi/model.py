from dataclasses import dataclass
from functools import reduce
from typing import Generic, Protocol, Sequence, TypeAlias, TypeVar, cast, overload

Number = TypeVar("Number", int, float)


@dataclass(frozen=True)
class Vec2(Generic[Number]):
    x: Number
    y: Number

    def __add__(self, other: "Vec2[Number]") -> "Vec2[Number]":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2[Number]") -> "Vec2[Number]":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2[float]":
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> "Vec2[float]":
        return Vec2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> "Vec2[float]":
        return Vec2(-self.x, -self.y)


WorldCoords: TypeAlias = Vec2[float]
PixelCoords: TypeAlias = Vec2[int]
TransformMatrix: TypeAlias = tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]


@overload
def _multiply(
    lhs: TransformMatrix, rhs: TransformMatrix
) -> TransformMatrix:
    ...


@overload
def _multiply(lhs: TransformMatrix, rhs: Vec2[float]) -> Vec2[float]:
    ...


def _multiply(
    lhs: TransformMatrix, rhs: TransformMatrix | Vec2[float]
) -> TransformMatrix | Vec2[float]:
    lhs_lines = lhs
    rhs_columns = list(zip(*rhs)) if isinstance(rhs, tuple) else [(rhs.x, rhs.y, 1)]

    result = tuple(
        tuple(sum(a * b for a, b in zip(line, column)) for column in rhs_columns)
        for line in lhs_lines
    )
    assert len(result) == 3

    if isinstance(rhs, Vec2):
        assert all(len(row) == 1 for row in result)
        x, y, one = (row[0] for row in result)
        assert one == 1
        return Vec2(x, y)

    assert all(len(row) == 3 for row in result)
    return cast(TransformMatrix, result)


def compose_transforms(
    matrices: Sequence[TransformMatrix]
) -> TransformMatrix:
    return reduce(_multiply, reversed(matrices))


def apply_transform(
    point: WorldCoords, matrix: TransformMatrix
) -> WorldCoords:
    return _multiply(matrix, point)


class DrawContext(Protocol):
    def draw_point(self, point: WorldCoords, color: str) -> None:
        ...

    def draw_line(self, start: WorldCoords, end: WorldCoords, color: str) -> None:
        ...


class Drawable(Protocol):
    name: str
    color: str

    def draw(self, ctx: DrawContext) -> None:
        ...

    def apply_transform(self, matrix: TransformMatrix) -> None:
        ...

    def get_center(self) -> WorldCoords:
        ...


@dataclass
class Point:
    name: str
    color: str
    position: WorldCoords

    def draw(self, ctx: DrawContext) -> None:
        ctx.draw_point(self.position, color=self.color)

    def apply_transform(self, matrix: TransformMatrix) -> None:
        self.position = apply_transform(self.position, matrix)

    def get_center(self) -> WorldCoords:
        return self.position


@dataclass
class Line:
    name: str
    color: str
    start: WorldCoords
    end: WorldCoords

    def draw(self, ctx: DrawContext) -> None:
        ctx.draw_line(self.start, self.end, color=self.color)

    def apply_transform(self, matrix: TransformMatrix) -> None:
        self.start = apply_transform(self.start, matrix)
        self.end = apply_transform(self.end, matrix)

    def get_center(self) -> WorldCoords:
        return (self.start + self.end) / 2


@dataclass
class Polygon:
    name: str
    color: str
    points: list[WorldCoords]

    def draw(self, ctx: DrawContext) -> None:
        for start, end in zip(self.points, self.points[1:]):
            ctx.draw_line(start, end, color=self.color)
        ctx.draw_line(self.points[-1], self.points[0], color=self.color)

    def apply_transform(self, matrix: TransformMatrix) -> None:
        self.points = [apply_transform(point, matrix) for point in self.points]

    def get_center(self) -> WorldCoords:
        return sum(self.points, start=Vec2(0.0, 0.0)) / len(self.points)
