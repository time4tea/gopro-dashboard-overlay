from geographiclib.geodesic import Geodesic

from .units import units


def process_ses(new, key, alpha=0.4):
    forecast = []
    previous = [None]

    def ses(item):
        current = key(item)
        try:
            if forecast:
                predicted = alpha * previous[0] + (1 - alpha) * forecast[-1]
                forecast.append(predicted)
                return {new: predicted}
            else:
                forecast.append(current)
                return {new: current}
        finally:
            previous[0] = current

    return ses


def calculate_speeds():
    def accept(a, b, c):
        assert c == 1
        inverse = Geodesic.WGS84.Inverse(a.point.lat, a.point.lon, b.point.lat, b.point.lon)
        dist = units.Quantity(inverse['s12'], units.m)
        time = units.Quantity((b.dt - a.dt).total_seconds(), units.seconds)
        azi = units.Quantity(inverse['azi1'], units.degree)
        speed = dist / time

        return {
            "speed": speed,
            "dist": dist,
            "time": time,
            "azi": azi,
        }

    return accept


def calculate_odo():
    total = [units.Quantity(0.0, units.m)]

    def accept(e):
        if e.dist is not None:
            total[0] += e.dist
        return {"odo": total[0]}

    return accept


def calculate_gradient():
    def accept(a, b, c):
        gain = b.alt - a.alt
        if a.odo and b.odo:
            dist = b.odo - a.odo
            if dist and dist.magnitude > 0:
                return {"grad": (gain / dist) * 100.0}

    return accept
