# No real idea if this is correct implementation!
# Found on the internet at: https://www.youtube.com/watch?v=ruB917YmtgE

class Kalman:

    def __init__(self):
        self.R = 100
        self.H = 1.00
        self.Q = 10
        self.P = 0
        self.U_hat = 0
        self.K = 0

    def update(self, U):
        if U is None:
            U = 0.0

        self.K = self.P * self.H / (self.H * self.P * self.H + self.R)
        self.U_hat = self.U_hat + self.K * (U - self.H * self.U_hat)
        self.P = (1 - self.K * self.H) * self.P + self.Q
        return self.U_hat


class SimpleExponential:

    def __init__(self, alpha=0.4):
        self.previous = None
        self.forecast = None
        self.alpha = alpha

    def update(self, current):
        if current is None:
            current = 0.0
        try:
            if self.forecast:
                predicted = self.alpha * self.previous + (1 - self.alpha) * self.forecast
                self.forecast = predicted
                return predicted
            else:
                self.forecast = current
                return current
        finally:
            self.previous = current
