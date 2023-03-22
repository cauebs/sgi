from dataclasses import dataclass, field
from itertools import count
from typing import TYPE_CHECKING, Iterable, Optional

from .model import Drawable, Line, PixelCoords, Point, Polygon, Vec2, WorldCoords

if TYPE_CHECKING:
    from .view import GraphicalViewer


@dataclass
class Controller:
    _window_pos: WorldCoords = Vec2(0, 0)
    _window_size: WorldCoords = Vec2(1, 1)
    _display_file: list[Drawable] = field(default_factory=list)
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
        self._graphical_viewer.repaint(self._display_file)

    def pan_window(self, delta: PixelCoords) -> None:
        self._window_pos += self.scale_viewport_vec_to_world(delta)
        self._update_view()

    def zoom_window(self, zoom_center: PixelCoords, amount: float) -> None:
        zoom_center_before = self.apply_inverse_viewport_transform(zoom_center)
        self._window_size = Vec2(
            self._window_size.x * (1 + amount),
            self._window_size.y * (1 + amount),
        )
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
            if all(drawable.name != name for drawable in self._display_file):
                return name
        assert False

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
            y=-window_pos.y + 1 - point.y / viewport_size.y * window_size.y,
        )

    def scale_viewport_vec_to_world(self, v: Vec2[int]) -> Vec2[float]:
        assert self._graphical_viewer is not None
        return Vec2(
            x=v.x / self._graphical_viewer.viewport_size.x * self._window_size.x,
            y=-v.y / self._graphical_viewer.viewport_size.y * self._window_size.y,
        )
