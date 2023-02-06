import dataclasses


@dataclasses.dataclass(frozen=True)
class Box:
    x1: float
    y1: float
    x2: float
    y2: float


def abox(x1, y1, x2, y2):
    return Box(x1, y1, x2, y2)
