from collections import Counter


class ReasonCounter(Counter):
    def because(self, reason):
        self.update({reason, 1})

    def inc(self, reason):
        return lambda: self.because(reason)