import re
from dataclasses import dataclass, field
from itertools import chain
import tkinter
import tkinter.simpledialog
import tkinter.ttk
import tkinter.messagebox
from typing import Iterable

from .controller import Controller, RotationCenter
from .model import Drawable, PixelCoords, Vec2, WorldCoords


def _split_points_into_lines(raw_text: str) -> str:
    return re.sub(r"(?<=\)), ?(?=\()", "\n", raw_text)


def _parse_vec(raw_text: str) -> WorldCoords:
    x, y = (float(coord) for coord in raw_text.strip("( )").split(","))
    return Vec2(x, y)


@dataclass
class GraphicalViewer:
    _controller: Controller
    viewport_size: PixelCoords
    _app_window: tkinter.Tk = field(default_factory=tkinter.Tk)
    _canvas: tkinter.Canvas = field(init=False)
    _zoom_amount: float = 0.1
    _pan_amount: int = 10
    _rotation_degrees: int = 15

    def __post_init__(self) -> None:
        self._app_window.title("SGI")

        self._canvas = tkinter.Canvas(
            self._app_window,
            width=self.viewport_size.x,
            height=self.viewport_size.y,
            background="black",
        )
        self._canvas.pack()
        self.bind_keys()

        self._controller.set_graphical_viewer(self)

    def _handle_scroll(self, event: tkinter.Event) -> None:  # type: ignore[type-arg]
        if event.num == 5 or event.delta == -120:
            amount = 0.1
        elif event.num == 4 or event.delta == 120:
            amount = -0.1
        else:
            return
        self._controller.zoom_window(Vec2(event.x, event.y), amount)

    def bind_keys(self) -> None:
        root = self._app_window
        controller = self._controller

        root.bind("<MouseWheel>", self._handle_scroll)
        root.bind("<Button-4>", self._handle_scroll)
        root.bind("<Button-5>", self._handle_scroll)

        amount = self._pan_amount
        root.bind("w", lambda _: controller.pan_window(Vec2(0, amount)))
        root.bind("a", lambda _: controller.pan_window(Vec2(-amount, 0)))
        root.bind("s", lambda _: controller.pan_window(Vec2(0, -amount)))
        root.bind("d", lambda _: controller.pan_window(Vec2(amount, 0)))

        root.bind("z", lambda _: controller.rotate_window(-self._rotation_degrees))
        root.bind("x", lambda _: controller.rotate_window(self._rotation_degrees))

        root.bind("c", lambda _: self.show_color_dialog())

        root.bind("o", lambda _: self.show_add_point_dialog())
        root.bind("l", lambda _: self.show_add_line_dialog())
        root.bind("p", lambda _: self.show_add_polygon_dialog())

        root.bind("e", lambda _: ScalingDialog(root, controller))
        root.bind("r", lambda _: RotationDialog(root, controller))
        root.bind("t", lambda _: TranslationDialog(root, controller))

    def show_color_dialog(self) -> None:
        color = tkinter.simpledialog.askstring(
            "Definir cor",
            "Insira uma cor para ser usada nos próximos objetos criados "
            "(e.g. '#fff', '#abcdef', 'green'):",
            initialvalue="white",
            parent=self._app_window,
        )
        if not color:
            return

        self._controller.set_color(color)

    def show_add_point_dialog(self) -> None:
        raw_text = tkinter.simpledialog.askstring(
            "Adicionar ponto",
            "Insira as coordenadas no formato '(x, y)':",
            parent=self._app_window,
        )
        if not raw_text:
            return

        self._controller.create_point(_parse_vec(raw_text))

    def show_add_line_dialog(self) -> None:
        raw_text = tkinter.simpledialog.askstring(
            "Adicionar linha",
            "Insira as coordenadas no formato '(x1, y1), (x2, y2)':",
            parent=self._app_window,
        )
        if not raw_text:
            return

        start, end = _split_points_into_lines(raw_text).splitlines()
        self._controller.create_line(_parse_vec(start), _parse_vec(end))

    def show_add_polygon_dialog(self) -> None:
        raw_text = tkinter.simpledialog.askstring(
            "Adicionar polígono",
            "Insira as coordenadas no formato '(x1, y1), (x2, y2), ...':",
            parent=self._app_window,
        )
        if not raw_text:
            return

        points = (
            _parse_vec(p) for p in _split_points_into_lines(raw_text).splitlines()
        )
        self._controller.create_polygon(points)

    def repaint(self, drawables: Iterable[Drawable]) -> None:
        self._canvas.delete("all")
        for drawable in drawables:
            drawable.draw(self)

    def draw_point(self, point: WorldCoords, color: str) -> None:
        coords = self._controller.apply_viewport_transform(point)
        self._canvas.create_oval(
            coords.x - 1,
            coords.y - 1,
            coords.x + 1,
            coords.y + 1,
            fill=color,
        )

    def draw_line(self, start: WorldCoords, end: WorldCoords, color: str) -> None:
        points = [
            self._controller.apply_viewport_transform(point) for point in [start, end]
        ]
        coordinates = [(p.x, p.y) for p in points]

        self._canvas.create_line(*chain.from_iterable(coordinates), fill=color)

    def run(self) -> None:
        self._app_window.mainloop()


def make_object_selector(
    parent: tkinter.Misc, object_names: Iterable[str]
) -> tkinter.Entry:
    tkinter.Label(parent, text="Objeto:").grid(row=0, sticky=tkinter.E)
    object_selector = tkinter.ttk.Combobox(parent, values=list(object_names))
    object_selector.grid(row=0, column=1, sticky=tkinter.W)
    return object_selector


def show_invalid_object_name_warning(parent: tkinter.Misc) -> None:
    tkinter.messagebox.showwarning(
        "Nome inválido",
        "Selecione um nome de objeto válido a partir da lista.",
        parent=parent,
    )


class ScalingDialog(tkinter.simpledialog.Dialog):
    def __init__(self, parent: tkinter.Misc, controller: Controller) -> None:
        self._controller = controller
        tkinter.simpledialog.Dialog.__init__(self, parent, "Escalonar")

    def body(self, parent: tkinter.Misc) -> tkinter.Misc:
        self.object_selector = make_object_selector(
            parent, self._controller.get_object_names()
        )

        tkinter.Label(parent, text="Fator de escala:").grid(row=1, sticky=tkinter.E)
        self.scale_factor_input = tkinter.Entry(parent)
        self.scale_factor_input.grid(row=1, column=1, sticky=tkinter.W)

        return self.object_selector

    def validate(self) -> bool:
        if self.object_selector.get() not in self._controller.get_object_names():
            show_invalid_object_name_warning(self)
            return False

        factor_raw = self.scale_factor_input.get()
        try:
            float(factor_raw)
        except ValueError:
            try:
                _parse_vec(factor_raw)
            except ValueError:
                tkinter.messagebox.showwarning(
                    "Fator inválido",
                    "O fator de escala deve ser um número real.",
                    parent=self,
                )
                return False

        return True

    def apply(self) -> None:
        selected_name = self.object_selector.get()
        factor_raw = self.scale_factor_input.get()
        try:
            scalar = float(factor_raw)
            scale_factor = Vec2(scalar, scalar)
        except ValueError:
            scale_factor = _parse_vec(factor_raw)

        self._controller.scale_object(selected_name, scale_factor)


class RotationDialog(tkinter.simpledialog.Dialog):
    def __init__(self, parent: tkinter.Misc, controller: Controller) -> None:
        self._controller = controller
        tkinter.simpledialog.Dialog.__init__(self, parent, "Rotacionar")

    def body(self, parent: tkinter.Misc) -> tkinter.Misc:
        self.object_selector = make_object_selector(
            parent, self._controller.get_object_names()
        )

        tkinter.Label(parent, text="Centro da rotação:").grid(row=1, sticky=tkinter.E)
        self.center_input = tkinter.ttk.Combobox(
            parent, values=[x.value for x in RotationCenter]
        )
        self.center_input.current(0)
        self.center_input.grid(row=1, column=1, sticky=tkinter.W)

        tkinter.Label(parent, text="Ângulo:").grid(row=2, sticky=tkinter.E)
        self.angle_input = tkinter.Entry(parent)
        self.angle_input.grid(row=2, column=1, sticky=tkinter.W)

        return self.object_selector

    def validate(self) -> bool:
        if self.object_selector.get() not in self._controller.get_object_names():
            show_invalid_object_name_warning(self)
            return False

        center_of_rotation = self.center_input.get()
        try:
            RotationCenter(center_of_rotation)
        except ValueError:
            try:
                _parse_vec(center_of_rotation)
            except ValueError:
                tkinter.messagebox.showwarning(
                    "Centro de rotação inválido",
                    "O centro deve ser um dos valores da lista ou um ponto '(x, y)'.",
                    parent=self,
                )
                return False

        try:
            float(self.angle_input.get())
        except ValueError:
            tkinter.messagebox.showwarning(
                "Ângulo inválido",
                "O ângulo deve ser um número real.",
                parent=self,
            )
            return False

        return True

    def apply(self) -> None:
        selected_name = self.object_selector.get()
        center_raw = self.center_input.get()
        angle = float(self.angle_input.get())

        center_of_rotation: RotationCenter | WorldCoords
        try:
            center_of_rotation = RotationCenter(center_raw)
        except ValueError:
            center_of_rotation = _parse_vec(center_raw)

        self._controller.rotate_object(selected_name, center_of_rotation, angle)


class TranslationDialog(tkinter.simpledialog.Dialog):
    def __init__(self, parent: tkinter.Misc, controller: Controller) -> None:
        self._controller = controller
        tkinter.simpledialog.Dialog.__init__(self, parent, "Transladar")

    def body(self, parent: tkinter.Misc) -> tkinter.Misc:
        self.object_selector = make_object_selector(
            parent, self._controller.get_object_names()
        )

        tkinter.Label(parent, text="Deslocamento (x, y):").grid(row=1, sticky=tkinter.E)
        self.delta_input = tkinter.Entry(parent)
        self.delta_input.grid(row=1, column=1, sticky=tkinter.W)

        return self.object_selector

    def validate(self) -> bool:
        if self.object_selector.get() not in self._controller.get_object_names():
            show_invalid_object_name_warning(self)
            return False

        try:
            _parse_vec(self.delta_input.get())
        except ValueError:
            tkinter.messagebox.showwarning(
                "Vetor inválido",
                "O deslocamento deve ser um vetor na forma '(x, y)'.",
                parent=self,
            )
            return False

        return True

    def apply(self) -> None:
        selected_name = self.object_selector.get()
        delta = _parse_vec(self.delta_input.get())
        self._controller.translate_object(selected_name, delta)
