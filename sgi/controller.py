from dataclasses import dataclass, field
from enum import Enum
from itertools import count
from math import cos, sin, radians
from typing import TYPE_CHECKING, Iterable, Optional

from .model import Drawable, Line, PixelCoords, Point, Polygon, Vec2, WorldCoords

if TYPE_CHECKING:
    from .view import GraphicalViewer


class RotationCenter(Enum):
    OBJECT_CENTER = "centro do objeto"
    ORIGIN = "origem"


@dataclass
class Controller:
    _window_pos: WorldCoords = Vec2(0, 0)
    _window_size: WorldCoords = Vec2(1, 1)
    _display_file: dict[str, Drawable] = field(default_factory=dict)
    _graphical_viewer: Optional["GraphicalViewer"] = None
    _original_window_pos: WorldCoords = field(init=False)
    _original_window_size: WorldCoords = field(init=False)

    def __post_init__(self) -> None:
        self._original_window_pos = self._window_pos
        self._original_window_size = self._window_size

    def set_graphical_viewer(self, viewer: "GraphicalViewer") -> None:
        self._graphical_viewer = viewer
        self._update_view()

    def _update_view(self) -> None:
        assert self._graphical_viewer is not None
        self._graphical_viewer.repaint(self._display_file.values())

    def pan_window(self, delta: PixelCoords) -> None:
        self._window_pos += self.scale_viewport_vec_to_world(delta)
        self._update_view()

    def zoom_window(self, zoom_center: PixelCoords, amount: float) -> None:
        zoom_center_before = self.apply_inverse_viewport_transform(zoom_center)
        self._window_size *= (1 + amount)
        zoom_center_after = self.apply_inverse_viewport_transform(zoom_center)
        pan_correction = zoom_center_after - zoom_center_before
        self._window_pos -= Vec2(pan_correction.x, -pan_correction.y)
        self._update_view()

    def reset_window(self, scale: float) -> None:
        self._window_pos = self._original_window_pos
        self._window_size = self._original_window_size
        self._update_view()

    def _find_unused_name(self, prefix: str) -> str:
        for i in count(start=1):
            name = f"{prefix} {i}"
            if name not in self._display_file:
                return name
        assert False

    def get_object_names(self) -> Iterable[str]:
        return self._display_file.keys()

    def create_point(self, coordinates: WorldCoords) -> Point:
        name = self._find_unused_name("Ponto")
        point = Point(name, coordinates)
        self._display_file.append(point)
        self._update_view()
        return point

    def create_line(self, start: WorldCoords, end: WorldCoords) -> Line:
        name = self._find_unused_name("Reta")
        line = Line(name, start, end)
        self._display_file.append(line)
        self._update_view()
        return line

    def create_polygon(self, points: Iterable[WorldCoords]) -> Polygon:
        name = self._find_unused_name("Polígono")
        polygon = Polygon(name, list(points))
        self._display_file.append(polygon)
        self._update_view()
        return polygon

    def scale_object(self, obj: str | Drawable, scale_factors: Vec2[float]) -> None:
        x = scale_factors.x
        y = scale_factors.y
        matrix = (
            (x, 0, 0),
            (0, y, 0),
            (0, 0, 1),
        )

        if isinstance(obj, str):
            obj = self._display_file[obj]

        obj.apply_transformation(matrix)
        self._update_view()

    def rotate_object(
        self,
        obj: str | Drawable,
        center_of_rotation: RotationCenter | WorldCoords,
        angle: float,
    ) -> None:
        if isinstance(obj, str):
            obj = self._display_file[obj]

        if center_of_rotation is not RotationCenter.ORIGIN:
            if center_of_rotation is RotationCenter.OBJECT_CENTER:
                center_of_rotation = obj.get_center()
            self.translate_object(obj, -center_of_rotation)

        c = cos(radians(angle))
        s = sin(radians(angle))
        matrix = (
            (c, -s, 0),
            (s, c, 0),
            (0, 0, 1),
        )
        obj.apply_transformation(matrix)

        if center_of_rotation is not RotationCenter.ORIGIN:
            self.translate_object(obj, center_of_rotation)

        self._update_view()

    def translate_object(self, obj: str | Drawable, delta: WorldCoords) -> None:
        x = delta.x
        y = delta.y
        matrix = (
            (1, 0, 0),
            (0, 1, 0),
            (x, y, 1),
        )

        if isinstance(obj, str):
            obj = self._display_file[obj]

        obj.apply_transformation(matrix)
        self._update_view()

    def apply_viewport_transform(self, point: WorldCoords) -> PixelCoords:
        window_pos = self._window_pos
        window_size = self._window_size

        assert self._graphical_viewer is not None
        viewport_size = self._graphical_viewer.viewport_size

        return Vec2(
            x=int((point.x - window_pos.x) / window_size.x * viewport_size.x),
            y=int((1 - point.y - window_pos.y) / window_size.y * viewport_size.y),
        )

    def apply_inverse_viewport_transform(self, point: PixelCoords) -> WorldCoords:
        window_pos = self._window_pos
        window_size = self._window_size

        assert self._graphical_viewer is not None
        viewport_size = self._graphical_viewer.viewport_size

        return Vec2(
            x=point.x / viewport_size.x * window_size.x + window_pos.x,
            y=-(point.y / viewport_size.y * window_size.y + window_pos.y - 1),
        )

    def scale_viewport_vec_to_world(self, v: Vec2[int]) -> Vec2[float]:
        assert self._graphical_viewer is not None
        return Vec2(
            x=v.x / self._graphical_viewer.viewport_size.x * self._window_size.x,
            y=-v.y / self._graphical_viewer.viewport_size.y * self._window_size.y,
        )
