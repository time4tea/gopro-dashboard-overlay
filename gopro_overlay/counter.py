from collections import Counter


class ReasonCounter(Counter):
    def because(self, reason: str):
        self.update({reason: 1})

    def inc(self, reason: str):
        return lambda: self.because(reason)
