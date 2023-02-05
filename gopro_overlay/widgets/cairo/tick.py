import dataclasses

from gopro_overlay.widgets.cairo.angle import Angle


@dataclasses.dataclass(frozen=True)
class TickParameters:
    step: Angle
    first: int = 0
    skipped: int = -1
