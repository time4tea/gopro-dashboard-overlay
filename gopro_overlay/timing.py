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
        return self.seconds / self.count

    def __str__(self):
        return f"Timer({self.name} - Called: {self.count}, Total: {self.seconds}, Avg: {self.avg})"
