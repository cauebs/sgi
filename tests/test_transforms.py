from dataclasses import astuple
from pytest import approx, fixture

from sgi.controller import (
    Controller,
    RotationCenter,
    make_rotation_matrix,
    make_scale_matrix,
    make_translate_matrix,
)
from sgi.model import (
    PixelCoords,
    Vec2,
    WorldCoords,
    apply_transform,
    compose_transforms,
)
from sgi.view import GraphicalViewer


@fixture
def hourglass_points() -> list[WorldCoords]:
    return [
        Vec2(0.2, 0.2),
        Vec2(0.8, 0.2),
        Vec2(0.6, 0.5),
        Vec2(0.8, 0.8),
        Vec2(0.2, 0.8),
        Vec2(0.4, 0.5),
    ]


@fixture
def controller() -> Controller:
    controller = Controller()
    GraphicalViewer(controller, viewport_size=PixelCoords(500, 500))
    return controller


def test_compose_transform_matrix() -> None:
    matrix = compose_transforms(
        [
            make_scale_matrix(Vec2(2, 2)),
            make_translate_matrix(Vec2(10, 0)),
        ]
    )

    assert matrix[0] == approx((2, 0, 10))
    assert matrix[1] == approx((0, 2, 0))
    assert matrix[2] == approx((0, 0, 1))


def test_apply_transform_matrix() -> None:
    matrix = make_rotation_matrix(30)
    point = Vec2(0.2, 0.2)

    new_point = apply_transform(point, matrix)
    assert astuple(new_point) == approx(
        (
            0.07320508075688772,
            0.27320508075688776,
        )
    )


def test_scale_center(
    controller: Controller, hourglass_points: list[WorldCoords]
) -> None:
    polygon = controller.create_polygon(hourglass_points)

    center_before = polygon.get_center()
    controller.scale_object(polygon, Vec2(2, 2))
    center_after = polygon.get_center()

    assert astuple(center_after) == approx(astuple(center_before))


def test_rotate_around_center(
    controller: Controller, hourglass_points: list[WorldCoords]
) -> None:
    polygon = controller.create_polygon(hourglass_points)

    center_before = polygon.get_center()
    controller.rotate_object(polygon, RotationCenter.OBJECT_CENTER, 30)
    center_after = polygon.get_center()

    assert astuple(center_after) == approx(astuple(center_before))


def test_translate(
    controller: Controller, hourglass_points: list[WorldCoords]
) -> None:
    polygon = controller.create_polygon(hourglass_points)
    delta = Vec2(0.5, 0.5)
    controller.translate_object(polygon, delta)

    for point, initial in zip(polygon.points, hourglass_points):
        assert astuple(point) == approx(astuple(initial + delta))


def test_viewport_transform_roundtrip(
    controller: Controller, hourglass_points: list[WorldCoords]
) -> None:
    for point in hourglass_points:
        new_point = controller.apply_inverse_viewport_transform(
            controller.apply_viewport_transform(point)
        )

        assert astuple(new_point) == approx(astuple(point), abs=3e-3)


def test_zoom_center(controller: Controller) -> None:
    viewport_center = controller.apply_viewport_transform(WorldCoords(0.5, 0.5))
    controller.zoom_window(zoom_center=viewport_center, amount=1)

    point_under_viewport_center = controller.apply_inverse_viewport_transform(
        viewport_center
    )

    assert astuple(point_under_viewport_center) == approx((0.5, 0.5))
