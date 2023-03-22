from .controller import Controller
from .model import PixelCoords
from .view import GraphicalViewer


def main() -> None:
    controller = Controller()
    app = GraphicalViewer(controller, viewport_size=PixelCoords(500, 500))
    app.run()
