from pytest import approx, fixture

from sgi.controller import Controller
from sgi.model import PixelCoords, Vec2, WorldCoords
from sgi.view import GraphicalViewer


@fixture
def controller() -> Controller:
    controller = Controller()
    GraphicalViewer(controller, viewport_size=PixelCoords(500, 500))
    return controller


def test_viewport_transform_roundtrip(controller: Controller) -> None:
    for x, y in [
        (0.2, 0.2),
        (0.8, 0.2),
        (0.6, 0.5),
        (0.8, 0.8),
        (0.2, 0.8),
        (0.4, 0.5),
    ]:
        point = Vec2(x, y)
        new_point = controller.apply_inverse_viewport_transform(
            controller.apply_viewport_transform(point)
        )

        assert new_point.x == approx(point.x)
        assert new_point.y == approx(point.y)


def test_zoom_center(controller: Controller) -> None:
    viewport_center = controller.apply_viewport_transform(WorldCoords(0.5, 0.5))
    controller.zoom_window(zoom_center=viewport_center, amount=1)

    point_under_viewport_center = controller.apply_inverse_viewport_transform(
        viewport_center
    )

    assert point_under_viewport_center.x == approx(0.5)
    assert point_under_viewport_center.y == approx(0.5)
