from dataclasses import dataclass
from typing import Generic, Protocol, TypeAlias, TypeVar

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
TransformationMatrix: TypeAlias = tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]


def apply_transformation(
    point: WorldCoords, matrix: TransformationMatrix
) -> WorldCoords:
    line = [point.x, point.y, 1]
    columns = zip(*matrix)
    x, y, one = [sum(a * b for a, b in zip(line, column)) for column in columns]
    assert one == 1
    return Vec2(x, y)


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

    def apply_transformation(self, matrix: TransformationMatrix) -> None:
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

    def apply_transformation(self, matrix: TransformationMatrix) -> None:
        self.position = apply_transformation(self.position, matrix)

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

    def apply_transformation(self, matrix: TransformationMatrix) -> None:
        self.start = apply_transformation(self.start, matrix)
        self.end = apply_transformation(self.end, matrix)

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

    def apply_transformation(self, matrix: TransformationMatrix) -> None:
        self.points = [
            apply_transformation(point, matrix)
            for point in self.points
        ]

    def get_center(self) -> WorldCoords:
        return sum(self.points, start=Vec2(0., 0.)) / len(self.points)
