from geographiclib.geodesic import Geodesic

from .gpmd import XYZ
from .smoothing import Kalman, SimpleExponential
from .units import units


# this is almost certainly wrong? - we are treating this as 3x1D samples, but its not.
def process_kalman_xyz(new, key):
    kx = Kalman()
    ky = Kalman()
    kz = Kalman()

    def process(item):
        xyz = key(item)
        return {new: XYZ(
            x=kx.update(xyz.x),
            y=ky.update(xyz.y),
            z=kz.update(xyz.z)
        )}

    return process


def process_ses(new, key, alpha=0.4):
    ses = SimpleExponential(alpha=alpha)

    def process(item):
        return {new: ses.update(key(item))}

    return process


def calculate_speeds():
    def accept(a, b, c):
        inverse = Geodesic.WGS84.Inverse(a.point.lat, a.point.lon, b.point.lat, b.point.lon)
        dist = units.Quantity(inverse['s12'], units.m)
        time = units.Quantity((b.dt - a.dt).total_seconds(), units.seconds)
        raw_azi = inverse['azi1']
        azi = units.Quantity(raw_azi, units.degree)

        raw_cog = 0 + raw_azi if raw_azi >= 0 else 360 + raw_azi
        cog = units.Quantity(raw_cog, units.degree)

        speed = dist / time

        return {
            "cspeed": speed,
            "dist": dist / c,  # suspect this isn't right!
            "time": time,
            "azi": azi,
            "cog": cog
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
    # have to move a bit (0.10m) to calculate decent gradient
    # this is called for frames ~2 sec apart.
    def accept(a, b, c):
        if a.alt and b.alt:
            gain = b.alt - a.alt
            if a.odo and b.odo:
                dist = b.odo - a.odo
                if dist and dist.magnitude > 0.10:
                    return {"grad": (gain / dist) * 100.0}

    return accept
