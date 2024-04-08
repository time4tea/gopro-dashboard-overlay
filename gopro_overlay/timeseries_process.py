from geographiclib.geodesic import Geodesic

from .gpmf import GPS_FIXED_VALUES
from .point import PintPoint3, Point
from .smoothing import Kalman, SimpleExponential
from .units import units


# this is almost certainly wrong? - we are treating this as 3x1D samples, but it's not.
def process_kalman_pp3(new, key):
    kx = Kalman()
    ky = Kalman()
    kz = Kalman()

    def process(item):
        xyz = key(item)
        return {new: PintPoint3(
            x=kx.update(xyz.x),
            y=ky.update(xyz.y),
            z=kz.update(xyz.z)
        )}

    return process


def process_kalman(new, key):
    k = Kalman()

    def process(item):
        v = key(item)
        if v is not None:
            return {new: k.update(v)}

    return process


def process_ses(new, key, alpha=0.4):
    ses = SimpleExponential(alpha=alpha)

    def process(item):
        return {new: ses.update(key(item))}

    return process


def distance_azi_between(a: Point, b: Point):
    inverse = Geodesic.WGS84.Inverse(a.lat, a.lon, b.lat, b.lon)
    dist = units.Quantity(inverse['s12'], units.m)
    raw_azi = inverse['azi1']
    return dist, raw_azi


def calculate_speeds():

    k = Kalman()

    def accept(a, b, c):
        dist, raw_azi = distance_azi_between(a.point, b.point)

        time = units.Quantity((b.dt - a.dt).total_seconds(), units.seconds)
        azi = units.Quantity(raw_azi, units.degree)

        raw_cog = 0 + raw_azi if raw_azi >= 0 else 360 + raw_azi
        cog = units.Quantity(raw_cog, units.degree)

        speed = dist / time if time.magnitude > 0 else units.Quantity(0, units.mps)

        smoothed = k.update(speed)
        return {
            "cspeed": smoothed,
            "cspeed.k": smoothed,
            "cspeed.raw": speed,
            "dist": dist / c,  # suspect this isn't right!
            "time": time,
            "azi": azi,
            "cog": cog
        }

    return accept


def calculate_accel():
    def accept(a, b, c):
        time = units.Quantity((b.dt - a.dt).total_seconds(), units.seconds)
        
        if a.speed and b.speed and time:
            accel = (b.speed - a.speed) / time
        else:
            accel = units.Quantity(0, units.mps)
        return { "accel": accel }

    return accept


def calculate_odo():
    total = [units.Quantity(0.0, units.m)]

    def accept(e):
        if e.dist is not None:
            total[0] += e.dist
        return {"codo": total[0]}

    return accept


def filter_locked():
    fields = ["speed", "cspeed", "accel", "azi", "cog", "time", "dist", "grad", "cgrad", "alt"]

    def accept(e):
        if e.gpsfix not in GPS_FIXED_VALUES:
            return {f: None for f in fields}

    return accept


def calculate_gradient():
    # have to move a bit to calculate decent gradient
    # this is called for frames ~2 sec apart.
    def accept(a, b, c):
        if a.alt and b.alt:
            gain = b.alt - a.alt

            dist, _ = distance_azi_between(a.point, b.point)

            if dist and dist.magnitude > 1.0:
                grad = (gain / dist) * 100.0
                if abs(grad.magnitude) < 45:
                    field = "cgrad"
                else:
                    field = "bad_grad"

                return {
                    field: grad,
                    "grad_gain": gain,
                    "grad_dist": dist,
                    "grad_other_packet": b.packet,
                    "grad_other_packet_index": b.packet_index,
                }

    return accept


def transit_passthrough():
    def accept(e):
        return {
            "transit_previous_stop": e.transit_previous_stop,
            "transit_current_stop": e.transit_current_stop,
            "transit_next_stop": e.transit_next_stop,
        }

    return accept