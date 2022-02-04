from collections import namedtuple

Dimension = namedtuple("Dimension", ["x", "y"])


def dimension_from(s):
    components = list(map(int, s.split("x")))
    if len(components) != 2:
        raise ValueError("dimension should be in format XxY")
    return Dimension(components[0], components[1])
