import colorsys
import dataclasses
from typing import Tuple


@dataclasses.dataclass(frozen=True)
class HLSColour:
    h: float
    l: float
    s: float
    a: float

    def lighten(self, by: float) -> 'HLSColour':
        return HLSColour(self.h, min(self.l + by, 1.0), self.s, self.a)

    def darken(self, by: float) -> 'HLSColour':
        return HLSColour(self.h, max(self.l - by, 1.0), self.s, self.a)

    def rgb(self) -> 'Colour':
        r, g, b = colorsys.hls_to_rgb(self.h, self.l, self.s)
        return Colour(r, g, b, self.a)


@dataclasses.dataclass(frozen=True)
class Colour:
    r: float
    g: float
    b: float
    a: float = 1.0

    def rgba(self) -> Tuple[float, float, float, float]:
        return self.r, self.g, self.b, self.a

    def rgb(self) -> Tuple[float, float, float]:
        return self.r, self.g, self.b

    def hls(self) -> HLSColour:
        h, l, s = colorsys.rgb_to_hls(self.r, self.g, self.b)
        return HLSColour(h, l, s, self.a)

    def darken(self, by: float) -> 'Colour':
        return self.hls().darken(by).rgb()

    def lighten(self, by: float) -> 'Colour':
        return self.hls().lighten(by).rgb()

    def alpha(self, new_alpha: float):
        return Colour(self.r, self.g, self.b, new_alpha)


BLACK = Colour(0.0, 0.0, 0.0)
WHITE = Colour(1.0, 1.0, 1.0)
RED = Colour(1.0, 0.0, 0.0)
darkenBy = 1.0 / 3
lightenBy = 1.0 / 3
