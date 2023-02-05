import dataclasses


@dataclasses.dataclass(frozen=True)
class TickParameters:
    step: float
    first: int = 0
    skipped: int = -1
