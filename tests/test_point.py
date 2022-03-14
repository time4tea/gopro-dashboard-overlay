import pytest

from gopro_overlay.point import Point3, Quaternion


def test_point3_length():
    assert Point3(3, 4, 0).length() == 5
    assert Point3(3, 4, 10).length() == pytest.approx(11.18, 0.01)


def test_point3_equality():
    p1 = Point3(10, 11, 12)
    p2 = Point3(10, 11, 12)
    assert p1 == p2

    p3 = Point3(1, 2, 3)
    assert p1 != p3


def test_point3_dot():
    assert Point3(3, 4, 0).dot(Point3(0, 0, 0)) == 0


def test_point3_tuple():
    assert Point3(1, 2, 3).tuple() == (1, 2, 3)


def test_quaternion_equality():
    q1 = Quaternion(23, Point3(1, 2, 3))
    q2 = Quaternion(23, Point3(1, 2, 3))

    assert q1 == q2

    q3 = Quaternion(100, Point3(1, 2, 3))
    assert q1 != q3

    q4 = Quaternion(23, Point3(1, 2, 34))
    assert q1 != q4


def test_quaternion_identity_multiply():
    q1 = Quaternion(23, Point3(1, 2, 3))

    assert (q1 * Quaternion.identity()) == q1


def test_quaternion_inverse_multiply():
    q1 = Quaternion(23, Point3(1, 2, 3))

    assert (q1 * q1.invert()) == Quaternion.identity()


def test_quaternion_to_axis_angle():
    q = Quaternion(w=0.999877925962096,
                   v=Point3(x=0.010010071108127079, y=-0.0021668141727958007, z=0.009979552598651083))
    aa = q.to_axis_angle()

    print(aa)

    assert aa[0] == pytest.approx(0.03, abs=0.002)


def test_rotate_point_by_quaternion_identity():
    point = Point3(0, 0, 0)
    identity = Quaternion.identity()

    assert identity.rotate(point) == point


def test_rotate_point_by_quaternion():
    point = Point3(0, -1, 0)

    q_flat = Quaternion(
        w=1.0,
        v=Point3(x=-9.155552842799158e-05, y=-3.051850947599719e-05, z=0.0)
    )
    q_up = Quaternion(
        w=0.7003997924741355,
        v=Point3(x=-0.7137058626056704, y=0.0018616290780358287, z=-0.003021332438123722)
    )

    assert q_flat.rotate(point).tuple() == pytest.approx(point.tuple(), abs=0.01)
    assert q_up.rotate(point).tuple() == pytest.approx(Point3(0, 0, -1).tuple(), abs=0.02)
