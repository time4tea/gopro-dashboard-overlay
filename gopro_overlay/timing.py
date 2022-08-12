import contextlib
import time


class PoorTimer:

    def __init__(self, name, indent=0):
        self.name = name
        self.indent = indent
        self.total = 0
        self.count = 0

    def time(self, f):
        t = time.time_ns()
        r = f()
        self.total += (time.time_ns() - t)
        self.count += 1
        return r

    @contextlib.contextmanager
    def timing(self, doprint=True):
        t = time.time_ns()
        try:
            yield
        finally:
            self.total += (time.time_ns() - t)
            self.count += 1
            if doprint:
                print(self)

    @property
    def seconds(self):
        return self.total / (10 ** 9)

    @property
    def avg(self):
        if self.count > 0:
            return self.seconds / self.count
        else:
            return 0

    @property
    def rate(self):
        a = self.avg
        if a == 0:
            return 0
        return 1 / a

    def __str__(self):
        return f"{ ' ' * 4 * self.indent }Timer({self.name} - Called: {self.count:,.0f}, Total: {self.seconds:.5f}, " \
               f"Avg: {self.avg:.5f}, Rate: {self.rate:,.2f})"
