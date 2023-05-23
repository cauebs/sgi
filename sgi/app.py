from textwrap import dedent
from .controller import Controller
from .model import PixelCoords
from .view import GraphicalViewer


def main() -> None:
    controller = Controller()
    app = GraphicalViewer(controller, viewport_size=PixelCoords(500, 500))

    print(
        dedent(
            """
            Need help?
            - `C` to change the color used for new objects
            - `O` to add a point
            - `L` to add a line
            - `P` to add a polygon
            - `E` to select and scale an object
            - `R` to select and rotate an object
            - `T` to select and translate an object
            - `WASD` to pan
            - `Z` and `X` to rotate the view
            - Mouse wheel to zoom
            """
        ).strip()
    )

    app.run()
