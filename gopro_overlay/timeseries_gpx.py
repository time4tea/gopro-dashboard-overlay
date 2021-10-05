import gpxpy

from gopro_overlay.timeseries import Timeseries


def timeseries_to_gpx(ts: Timeseries):
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for entry in ts.items():
        gpx_segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                time=entry.dt,
                latitude=entry.point.lat,
                longitude=entry.point.lon,
                elevation=entry.alt.to("m").magnitude)
        )

    return gpx
