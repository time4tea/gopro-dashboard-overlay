import bisect
from pathlib import Path

import fitdecode

from gopro_overlay.entry import Entry
from gopro_overlay.gpmf import GPSFix
from gopro_overlay.point import Point
from gopro_overlay.timeseries import Timeseries


def garmin_to_gps(v):
    return v / ((2 ** 32) / 360)


interpret = {
    "position_lat": lambda v, u: {"lat": garmin_to_gps(v)},
    "position_long": lambda v, u: {"lon": garmin_to_gps(v)},
    "distance": lambda v, u: {"odo": u.Quantity(v, u.m)},
    "altitude": lambda v, u: {"alt": u.Quantity(v, u.m)},
    "enhanced_altitude": lambda v, u: {"alt": u.Quantity(v, u.m)},
    "speed": lambda v, u: {"speed": u.Quantity(v, u.mps)},
    "enhanced_speed": lambda v, u: {"speed": u.Quantity(v, u.mps)},
    "heart_rate": lambda v, u: {"hr": u.Quantity(v, u.bpm)},
    "cadence": lambda v, u: {"cad": u.Quantity(v, u.rpm)},
    "temperature": lambda v, u: {"atemp": u.Quantity(v, u.degC)},
    "gps_accuracy": lambda v, u: {"dop": u.Quantity(v)},
    "power": lambda v, u: {"power": u.Quantity(v, u.watt)},
    "grade": lambda v, u: {"grad": u.Quantity(v)},
    "Sdps": lambda v, u: {"sdps": u.Quantity(v, u.cm)},
    "rear_gear_num": lambda v, u: {"gear_rear": u.Quantity(v)},
    "front_gear_num": lambda v, u: {"gear_front": u.Quantity(v)},
    "unknown_108": lambda v, u: {"respiration": u.Quantity(v / 100, u.brpm)},
}


def load_timeseries(filepath: Path, units):
    ts = Timeseries()

    persistent_events = {}
    persistent_event_times = []

    last_ts_event = None

    with fitdecode.FitReader(filepath) as ff:
        for frame in (f for f in ff if f.frame_type == fitdecode.FIT_FRAME_DATA):

            if frame.name == 'record':
                entry = None
                items = {}

                for field in frame.fields:
                    if field.name == "timestamp":
                        # we should set the gps fix or Journey.accept() will skip the point:
                        entry = Entry(
                            dt=field.value,
                            gpsfix=GPSFix.LOCK_3D.value
                        )

                        # Now we need to see if there are relevant persistent events for us to copy in
                        if persistent_event_times:
                            relevant_persistent_event_index = bisect.bisect_right(persistent_event_times,
                                                                                  field.value) - 1
                            if relevant_persistent_event_index >= 0:
                                relevant_persistent_event_timestamp = persistent_event_times[
                                    relevant_persistent_event_index]
                                relevant_persistent_events = persistent_events[relevant_persistent_event_timestamp]
                                entry.update(**relevant_persistent_events)

                        last_ts_event = entry
                    else:
                        if field.name in interpret and field.value is not None:
                            items.update(**interpret[field.name](field.value, units))
                        elif field.value is not None and isinstance(field.value, (int, float)):
                            items[field.name] = units.Quantity(field.value)

                if "lat" in items and "lon" in items:
                    items["point"] = Point(lat=items["lat"], lon=items["lon"])
                    del (items["lat"])
                    del (items["lon"])

                # only use fit data items that have lat/lon
                if "point" in items:
                    entry.update(**items)
                    ts.add(entry)
            elif frame.name == 'event':

                event_frame = {fi.name: fi.value for fi in frame.fields}

                # this is pretty hacky - it will only work when the only events we care about have all the data fields
                if event_frame['event'] in {'front_gear_change', 'rear_gear_change'}:
                    # we want to consolidate this event with any other event we had at the same time
                    timestamp = event_frame['timestamp']
                    if timestamp in persistent_events:
                        item = persistent_events[timestamp]
                    else:
                        item = {}
                        persistent_events[timestamp] = item
                        persistent_event_times.append(timestamp)

                    for k in ['front_gear_num', 'rear_gear_num']:
                        if k in event_frame:
                            d = interpret[k](event_frame[k], units)
                            item.update(d)

                    if last_ts_event is not None:
                        if timestamp == last_ts_event.dt:
                            last_ts_event.update(**item)
            else:
                pass

    return ts
