import pytest

from gopro_overlay.dimensions import Dimension
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.text import CachingText, Text
from gopro_overlay.widgets.widgets import Composite, Translate, Frame
from tests import test_widgets_setup
from tests.approval import approve_image
from tests.test_widgets import time_rendering

font = test_widgets_setup.font

@pytest.mark.gfx
@approve_image
def test_frame_border_visible_over_content():
    return time_rendering(name="viewport", widgets=[
        Translate(
            Coordinate(10, 10),
            Frame(
                dimensions=Dimension(300, 200),
                opacity=0.6,
                fill=(0, 0, 0),
                outline=(255, 255, 255),
                child=CachingText(
                    at=Coordinate(-8, 0),
                    fill=(255, 255, 0),
                    value=lambda: "Hello",
                    font=font.font_variant(size=64)
                ),
            )
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_circular():
    return time_rendering(name="viewport", widgets=[
        Composite(
            Text(at=Coordinate(100, 150), value=lambda: "Partially Visible", font=font.font_variant(size=64)),
            Translate(
                Coordinate(100, 00),
                Frame(
                    dimensions=Dimension(200, 200),
                    opacity=0.6,
                    fill=(0, 0, 0),
                    outline=(255, 255, 255),
                    corner_radius=100,
                    child=CachingText(
                        at=Coordinate(0, 000),
                        fill=(255, 255, 0),
                        value=lambda: "Hello",
                        font=font.font_variant(size=128)
                    ),
                )
            )
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_clipping():
    return time_rendering(name="viewport", widgets=[
        Translate(
            Coordinate(10, 10),
            Frame(
                dimensions=Dimension(300, 200),
                opacity=0.5,
                outline=(255, 255, 255),
                fill=(0, 0, 0),
                corner_radius=30,
                child=Composite(
                    CachingText(at=Coordinate(250, -20), value=lambda: "Hello", font=font.font_variant(size=48)),
                    CachingText(at=Coordinate(-30, 50), value=lambda: "World", font=font.font_variant(size=48))
                )
            )
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_fill():
    return time_rendering(name="viewport", widgets=[
        Frame(
            dimensions=Dimension(300, 200),
            fill=(255, 255, 255)
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_fill_opacity():
    return time_rendering(name="viewport", widgets=[
        Frame(
            dimensions=Dimension(300, 200),
            fill=(255, 255, 255, 128),
            corner_radius=35
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_fill_cr():
    return time_rendering(name="viewport", widgets=[
        Frame(
            dimensions=Dimension(300, 200),
            fill=(255, 255, 255),
            corner_radius=35
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_fill_cr_outline():
    return time_rendering(name="viewport", widgets=[
        Frame(
            dimensions=Dimension(300, 200),
            fill=(255, 255, 255),
            outline=(255, 0, 0),
            corner_radius=35
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_fade_cr_zero():
    return time_rendering(name="viewport", widgets=[
        Frame(
            dimensions=Dimension(300, 200),
            fill=(255, 255, 255),
            child=Frame(
                dimensions=Dimension(300, 200),
                fill=(255, 0, 0),
                fade_out=50,
            )
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_fade_cr_zero_new():
    return time_rendering(name="viewport", widgets=[
        Frame(
            dimensions=Dimension(300, 200),
            fill=(255, 0, 0),
            fade_out=50,
        )
    ])


@pytest.mark.gfx
@approve_image
def test_frame_fade_cr_non_zero():
    return time_rendering(name="viewport", widgets=[
        Frame(
            dimensions=Dimension(300, 200),
            fill=(255, 255, 255),
            child=Frame(
                dimensions=Dimension(300, 200),
                corner_radius=100,
                fill=(255, 0, 0),
                fade_out=50,
            )
        )
    ])
