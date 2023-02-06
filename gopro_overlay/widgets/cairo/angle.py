import functools
import math


@functools.total_ordering
class Angle:

    def __init__(self, degrees: float = None, radians: float = None):
        if degrees is not None and radians is not None:
            raise ValueError("can't have both")

        if degrees is None and radians is None:
            raise ValueError("must have one")

        if degrees is not None:
            self.angle = math.radians(degrees)
        if radians is not None:
            self.angle = radians

    def degrees(self) -> float:
        return math.degrees(self.angle)

    def radians(self) -> float:
        return self.angle

    def __add__(self, other) -> 'Angle':
        if type(other) != Angle:
            return NotImplemented
        return Angle(radians=self.angle + other.angle)

    def __sub__(self, other) -> 'Angle':
        if type(other) != Angle:
            return NotImplemented
        return Angle(radians=self.angle - other.angle)

    def __truediv__(self, other) -> 'Angle':
        if type(other) == int:
            return Angle(radians=self.angle / other)
        if type(other) == float:
            return Angle(radians=self.angle / other)
        return NotImplemented

    def __mul__(self, other) -> 'Angle':
        if type(other) == int:
            return Angle(radians=self.angle * other)
        if type(other) == float:
            return Angle(radians=self.angle * other)
        return NotImplemented

    def __rmul__(self, other):
        if type(other) == int:
            return Angle(radians=self.angle * other)
        if type(other) == float:
            return Angle(radians=self.angle * other)
        return NotImplemented


    def __neg__(self):
        return Angle(radians=-self.angle)

    def __eq__(self, other):
        if type(other) != Angle:
            return NotImplemented
        return self.angle == other.angle

    def __le__(self, other):
        if type(other) != Angle:
            return NotImplemented
        return self.angle <= other.angle

    @staticmethod
    def zero():
        return Angle(degrees=0.0)

    @staticmethod
    def semicircle():
        return Angle(degrees=180)

    @staticmethod
    def fullcircle():
        return Angle(degrees=360)
