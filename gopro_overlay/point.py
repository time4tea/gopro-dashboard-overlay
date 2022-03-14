import math
from typing import Tuple


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return Coordinate(self.x * other, self.y * other)

    def __str__(self):
        return f"Coordinate(x={self.x}, y={self.y})"

    def tuple(self):
        return self.x, self.y


class Point:
    def __init__(self, lat, lon):
        self.lon = lon
        self.lat = lat

    def __sub__(self, other):
        return Point(self.lat - other.lat, self.lon - other.lon)

    def __add__(self, other):
        return Point(self.lat + other.lat, self.lon + other.lon)

    def __mul__(self, other):
        return Point(self.lat * other, self.lon * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        return f"Point(lat={self.lat}, lon={self.lon})"

    def __repr__(self):
        return str(self)


class Point3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def length(self) -> float:
        return math.sqrt(self.sum_squares())

    def sum_squares(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def __sub__(self, other: 'Point3') -> 'Point3':
        return Point3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other: 'Point3') -> 'Point3':
        return Point3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, multiplier: float) -> 'Point3':
        return Point3(self.x * multiplier, self.y * multiplier, self.z * multiplier)

    def __truediv__(self, divisor: float) -> 'Point3':
        return Point3(self.x / divisor, self.y / divisor, self.z / divisor)

    def __str__(self):
        return f"Point3(x={self.x}, y={self.y}, z={self.z})"

    def __eq__(self, other: 'Point3'):
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)

    def dot(self, other: 'Point3') -> float:
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def cross(self, other: 'Point3') -> 'Point3':
        return Point3(
            (self.y * other.z - self.z * other.y),
            (-(self.x * other.z - self.z * other.x)),
            (self.x * other.y - self.y * other.x)
        )

    def __repr__(self):
        return str(self)

    def tuple(self):
        return self.x, self.y, self.z


class Quaternion:
    '''
    quaternion implementation based on: https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    thanks to the author!, any errors my own
    '''

    def __init__(self, w: float, v: Point3):
        self.w = w
        self.v = v

    def __sub__(self, other: 'Quaternion') -> 'Quaternion':
        return Quaternion(self.w - other.w, self.v - other.v)

    def __add__(self, other: 'Quaternion') -> 'Quaternion':
        return Quaternion(self.w + other.w, self.v + other.v)

    def __mul__(self, multiplier: 'Quaternion') -> 'Quaternion':
        return Quaternion(
            self.w * multiplier.w - self.v.dot(multiplier.v),
            (multiplier.v * self.w) + (self.v * multiplier.w) + (self.v.cross(multiplier.v))
        )

    def __truediv__(self, divisor: float):
        return Quaternion(self.w / divisor, self.v / divisor)

    def __str__(self) -> str:
        return f"Quaternion(w={self.w},v={self.v})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: 'Quaternion'):
        return (self.w == other.w) and (self.v == other.v)

    def length(self) -> float:
        return math.sqrt(self.sum_squares())

    def sum_squares(self) -> float:
        return (self.w ** 2) + self.v.sum_squares()

    def conjugate(self) -> 'Quaternion':
        return Quaternion(self.w, self.v * -1)

    def invert(self) -> 'Quaternion':
        return self.conjugate() / self.sum_squares()

    @staticmethod
    def identity() -> 'Quaternion':
        return Quaternion(1, Point3(0, 0, 0))

    def to_axis_angle(self) -> Tuple:
        theta = 2.0 * math.acos(self.w)
        if theta != 0.0:
            return theta, self.v / math.sin(theta / 2.0)
        else:
            return 0.0, Point3(1, 0, 0)

    def rotate(self, point: Point3) -> Point3:
        return (self.invert() * (Quaternion(0, point) * self)).v
