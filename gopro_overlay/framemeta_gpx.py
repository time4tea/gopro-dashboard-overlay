import datetime
from datetime import timedelta

import gpxpy

from gopro_overlay.entry import Entry
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.timeseries import Timeseries
from gopro_overlay.timeunits import Timeunit, timeunits


def framemeta_to_gpx(fm: FrameMeta, step: timedelta = timedelta(seconds=0)):
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for entry in fm.items(step=step):
        entry_dt = entry.dt

        gpx_segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                time=entry_dt,
                latitude=entry.point.lat,
                longitude=entry.point.lon,
                elevation=entry.alt.to("m").magnitude)
        )

    return gpx


def merge_gpx_with_gopro(gpx_timeseries: Timeseries, gopro_framemeta: FrameMeta):
    # pretty hacky merge
    # assume that the GPS timestamps in gopro are basically correct.
    # overwrite the location with the interpolated location from GPX
    # copy over any other attributes that are there
    # if no entry for that time exists in the GPX file, just ignore.

    if gpx_timeseries.min > gopro_framemeta.get(gopro_framemeta.max).dt:
        raise ValueError("GPX file seems to start after the end of the video")

    if gpx_timeseries.max < gopro_framemeta.get(gopro_framemeta.min).dt:
        raise ValueError("GPX file seems to finish before the start of the video")

    def processor(gopro_entry: Entry):
        try:
            gpx_entry = gpx_timeseries.get(gopro_entry.dt)
            return gpx_entry.items
        except ValueError:
            pass

    gopro_framemeta.process(processor)


def timeseries_to_framemeta(gpx_timeseries: Timeseries, units, start_date: datetime.datetime = None, duration: Timeunit = None) -> FrameMeta:
    fake_frame_meta = FrameMeta()

    if start_date is None:
        start_date = gpx_timeseries.min

    if duration is None:
        end_date = gpx_timeseries.max
    else:
        end_date = start_date + duration.timedelta()

    stepper = gpx_timeseries.stepper(step=timeunits(seconds=0.1))

    for index, pts in enumerate(stepper.steps()):

        entry = gpx_timeseries.get(pts)

        point_datetime = entry.dt

        if point_datetime < start_date:
            continue
        if point_datetime > end_date:
            break

        offset = Timeunit.from_timedelta(point_datetime - start_date)

        fake_frame_meta.add(
            offset,
            Entry(
                dt=point_datetime,
                timestamp=units.Quantity(offset.millis(), units.number),
                dop=units.Quantity(10, units.number),
                packet=units.Quantity(index, units.number),
                packet_index=units.Quantity(0, units.number),
                **entry.items
            )
        )

    return fake_frame_meta
