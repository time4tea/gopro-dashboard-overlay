from gopro_overlay.gpmd import XYZ
from gopro_overlay.gpmd_visitors_xyz import ORIN


def apply_orin(orin, original):
    return ORIN(orin).apply(original)


def test_converting_initial_xyz_to_actual_with_orin_hero_9():
    orin = "ZXY"
    original = XYZ._make([1, 2, 3])

    reordered = apply_orin(orin, original)

    assert reordered.x == 2
    assert reordered.z == 1
    assert reordered.y == 3


def test_converting_initial_xyz_to_actual_with_orin_hero_6():
    orin = "YxZ"
    original = XYZ._make([1, 2, 3])

    reordered = apply_orin(orin, original)

    assert reordered.x == -2
    assert reordered.z == 3
    assert reordered.y == 1


def test_converting_initial_xyz_to_actual_with_orin_fusion():
    orin = "yXZ"
    original = XYZ._make([1, 2, 3])

    reordered = apply_orin(orin, original)

    assert reordered.x == 2
    assert reordered.z == 3
    assert reordered.y == -1


def test_converting_initial_xyz_to_actual_with_orin_hero8():
    orin = "zxY"
    original = XYZ._make([1, 2, 3])

    reordered = apply_orin(orin, original)

    assert reordered.x == -2
    assert reordered.z == -1
    assert reordered.y == 3
