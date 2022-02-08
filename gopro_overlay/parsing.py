
from datetime import datetime


def parse_time(s):
    for f in ["%H:%M:%S.%f", "%H:%M:%S", "%M:%S.%f", "%M:%S", "%S.%f", "%S"]:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            pass
    raise ValueError(f"Unable to parse '{s}' as a timey thing")
