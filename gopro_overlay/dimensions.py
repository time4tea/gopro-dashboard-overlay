from dataclasses import dataclass


@dataclass(frozen=True)
class Dimension:
    x: int
    y: int


def dimension_from(s):
    components = list(map(int, s.split("x")))
    if len(components) != 2:
        raise ValueError("dimension should be in format XxY")
    return Dimension(x=components[0], y=components[1])
