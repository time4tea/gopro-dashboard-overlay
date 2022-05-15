import datetime


class Timeunit:
    def __init__(self, us):
        self.us = int(us)

    def millis(self):
        return self.us / 1000

    def __abs__(self):
        return Timeunit(abs(self.us))

    def __add__(self, other):
        return Timeunit(self.us + other.us)

    def __sub__(self, other):
        return Timeunit(self.us - other.us)

    def __hash__(self):
        return self.us

    def __mul__(self, other):
        return Timeunit(self.us * other)

    def __rmul__(self, other):
        return Timeunit(self.us * other)

    def __truediv__(self, other):
        if type(other) == type(self):
            return self.us / other.us
        elif type(other) == int:
            return Timeunit(self.us / other)
        raise NotImplementedError(f"Unsupported / between {type(self)} and {type(other)}")

    def __eq__(self, other):
        return self.us == other.us

    def __lt__(self, other):
        return self.us < other.us

    def __gt__(self, other):
        return self.us > other.us

    def __le__(self, other):
        return self.us <= other.us

    def __ge__(self, other):
        return self.us >= other.us

    def __repr__(self):
        return f"Timeunit ms={self.us / 1000.0}"

    def align(self, other):
        return Timeunit((self.us // other.us) * other.us)

    def timedelta(self):
        return datetime.timedelta(microseconds=self.us)


multipliers = {
    "micros": 1,
    "millis": 1000,
    "seconds": 1000 * 1000,
    "minutes": 1000 * 1000 * 60,
    "hours": 1000 * 1000 * 60 * 60,
    "days": 1000 * 1000 * 60 * 60 * 24,
}


def timeunits(**kwargs):
    if len(kwargs) > 1:
        raise NotImplemented(f"Can only supply a single arg, not {kwargs}")
    for k, v in multipliers.items():
        if k in kwargs:
            return Timeunit(kwargs[k] * v)

    raise AttributeError(f"Arg {kwargs} not supported")
