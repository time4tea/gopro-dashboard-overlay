import datetime


class Timeunit:
    def __init__(self, us):
        self.us = int(us)

    def millis(self):
        return self.us / 1000

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

    def timedelta(self):
        return datetime.timedelta(microseconds=self.us)


def timeunits(**kwargs):
    if len(kwargs) > 1:
        raise NotImplemented(f"Can only supply a single arg, not {kwargs}")
    if "seconds" in kwargs:
        return Timeunit(kwargs["seconds"] * 1000 * 1000)
    elif "millis" in kwargs:
        return Timeunit(kwargs["millis"] * 1000)
    elif "micros" in kwargs:
        return Timeunit(kwargs["micros"])
    else:
        raise AttributeError(f"Arg {kwargs} not supported")
