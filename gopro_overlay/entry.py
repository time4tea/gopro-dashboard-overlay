from datetime import timedelta


class Entry:

    def __init__(self, dt, **kwargs):
        self.dt = dt
        self.items = {k: v for k, v in dict(**kwargs).items() if v is not None}

    def update(self, **kwargs):
        self.items.update(**kwargs)

    def __getattr__(self, item):
        return self.items.get(item, None)

    def __str__(self):
        return f"Entry: {self.dt} - {self.items}"

    def interpolate(self, other, dt):
        if self.dt == other.dt:
            raise ValueError(f"Cannot interpolate between equal points")
        if self.dt > other.dt:
            print(f"**Note** Requested interpolation [{self.dt} < *{dt}* < {other.dt}] : Lower point should be first - data out of order?")
            return other.interpolate(self, dt)
        if dt < self.dt:
            raise ValueError(f"Requested interpolation [{self.dt} < *{dt}* < {other.dt}] lies before this point [{self.dt}] (should be after)")
        if dt > other.dt:
            raise ValueError(f"Requested interpolation [{self.dt} < *{dt}* < {other.dt}] lies after other point [{other.dt}] (should be before)")

        if dt == self.dt:
            return self
        elif dt == other.dt:
            return other

        range = (other.dt - self.dt) / timedelta(milliseconds=1)
        point = (dt - self.dt) / timedelta(milliseconds=1)

        position = point / range

        items = {}
        for key in self.items.keys():
            start = self.items[key]
            try:
                end = other.items[key]
                diff = end - start
                interp = start + (diff * position)
            except KeyError:
                interp = None
            items[key] = interp

        return Entry(dt, **items)
