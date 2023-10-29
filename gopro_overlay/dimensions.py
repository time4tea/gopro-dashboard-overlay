from dataclasses import dataclass


@dataclass(frozen=True)
class Dimension:
    x: int
    y: int

    def tuple(self):
        return self.x, self.y

    def __truediv__(self, other):
        if type(other) == int:
            return Dimension(int(self.x / other), int(self.y / other))
        return NotImplemented


def dimension_from(s):
    components = list(map(int, s.split("x")))
    if len(components) != 2:
        raise ValueError("dimension should be in format XxY")
    return Dimension(x=components[0], y=components[1])
