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

    def __mul__(self, other: "Vec2[Number]") -> "Vec2[Number]":
        return Vec2(self.x * other.x, self.y * other.y)


WorldCoords: TypeAlias = Vec2[float]
PixelCoords: TypeAlias = Vec2[int]


class DrawContext(Protocol):
    def draw_point(self, point: WorldCoords) -> None:
        ...

    def draw_line(self, start: WorldCoords, end: WorldCoords) -> None:
        ...


class Drawable(Protocol):
    name: str

    def draw(self, ctx: DrawContext) -> None:
        ...


@dataclass
class Point:
    name: str
    position: WorldCoords

    def draw(self, ctx: DrawContext) -> None:
        ctx.draw_point(self.position)


@dataclass
class Line:
    name: str
    start: WorldCoords
    end: WorldCoords

    def draw(self, ctx: DrawContext) -> None:
        ctx.draw_line(self.start, self.end)


@dataclass
class Polygon:
    name: str
    points: list[WorldCoords]

    def draw(self, ctx: DrawContext) -> None:
        for start, end in zip(self.points, self.points[1:]):
            ctx.draw_line(start, end)
        ctx.draw_line(self.points[-1], self.points[0])
