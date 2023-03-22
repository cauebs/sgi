import re
from dataclasses import dataclass, field
from itertools import chain
from tkinter import Canvas, Event, Tk, simpledialog
from typing import Iterable

from .controller import Controller
from .model import Drawable, PixelCoords, Vec2, WorldCoords


def _split_points_into_lines(raw_text: str) -> str:
    return re.sub(r"(?<=\)), ?(?=\()", "\n", raw_text)


def _parse_point(raw_text: str) -> WorldCoords:
    x, y = (float(coord) for coord in raw_text.strip("( )").split(","))
    return Vec2(x, y)


@dataclass
class GraphicalViewer:
    _controller: Controller
    viewport_size: PixelCoords
    _window: Tk = field(default_factory=Tk)
    _canvas: Canvas = field(init=False)
    _zoom_amount: float = 0.1
    _pan_amount: int = 10

    def __post_init__(self) -> None:
        self._canvas = Canvas(
            self._window,
            width=self.viewport_size.x,
            height=self.viewport_size.y,
        )
        self._canvas.pack()
        self.bind_keys()

        self._controller.set_graphical_viewer(self)

    def bind_keys(self) -> None:
        self._window.bind("o", lambda _: self.add_point())
        self._window.bind("l", lambda _: self.add_line())
        self._window.bind("p", lambda _: self.add_polygon())

        pan_window = self._controller.pan_window
        self._window.bind("w", lambda _: pan_window(Vec2(0, self._pan_amount)))
        self._window.bind("a", lambda _: pan_window(Vec2(-self._pan_amount, 0)))
        self._window.bind("s", lambda _: pan_window(Vec2(0, -self._pan_amount)))
        self._window.bind("d", lambda _: pan_window(Vec2(self._pan_amount, 0)))

        def handle_scroll(event: Event) -> None:  # type: ignore[type-arg]
            if event.num == 5 or event.delta == -120:
                amount = 0.1
            elif event.num == 4 or event.delta == 120:
                amount = -0.1
            else:
                return
            self._controller.zoom_window(Vec2(event.x, event.y), amount)

        self._window.bind("<MouseWheel>", handle_scroll)
        self._window.bind("<Button-4>", handle_scroll)
        self._window.bind("<Button-5>", handle_scroll)

    def add_point(self) -> None:
        raw_text = simpledialog.askstring(
            "Adicionar ponto",
            "Insira as coordenadas no formato '(x, y)':",
            parent=self._window,
        )
        if raw_text is None:
            return

        self._controller.create_point(_parse_point(raw_text))

    def add_line(self) -> None:
        raw_text = simpledialog.askstring(
            "Adicionar linha",
            "Insira as coordenadas no formato '(x1, y1), (x2, y2)':",
            parent=self._window,
        )
        if raw_text is None:
            return

        start, end = _split_points_into_lines(raw_text).splitlines()
        self._controller.create_line(_parse_point(start), _parse_point(end))

    def add_polygon(self) -> None:
        raw_text = simpledialog.askstring(
            "Adicionar polígono",
            "Insira as coordenadas no formato '(x1, y1), (x2, y2), ...':",
            parent=self._window,
        )
        if raw_text is None:
            return

        points = (
            _parse_point(p) for p in _split_points_into_lines(raw_text).splitlines()
        )
        self._controller.create_polygon(points)

    def repaint(self, drawables: Iterable[Drawable]) -> None:
        self._canvas.delete("all")
        for drawable in drawables:
            drawable.draw(self)

    def draw_point(self, point: WorldCoords) -> None:
        coords = self._controller.apply_viewport_transform(point)
        self._canvas.create_oval(
            coords.x - 1,
            coords.y - 1,
            coords.x + 1,
            coords.y + 1,
            fill="black",
        )

    def draw_line(self, start: WorldCoords, end: WorldCoords) -> None:
        points = [
            self._controller.apply_viewport_transform(point) for point in [start, end]
        ]
        coordinates = [(p.x, p.y) for p in points]

        self._canvas.create_line(*chain.from_iterable(coordinates))

    def run(self) -> None:
        self._window.mainloop()
