import contextlib
import time


class PoorTimer:

    def __init__(self, name):
        self.name = name
        self.total = 0
        self.count = 0

    def time(self, f):
        t = time.time_ns()
        r = f()
        self.total += (time.time_ns() - t)
        self.count += 1
        return r

    @contextlib.contextmanager
    def timing(self):
        t = time.time_ns()
        try:
            yield
        finally:
            self.total += (time.time_ns() - t)
            self.count += 1
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
        return f"Timer({self.name} - Called: {self.count:,.0f}, Total: {self.seconds:.5f}, " \
               f"Avg: {self.avg:.5f}, Rate: {self.rate:,.2f})"
