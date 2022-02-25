import gpxpy

from gopro_overlay import gpx
from gopro_overlay.point import Point
from gopro_overlay.timeseries import Entry
from gopro_overlay.units import units
from tests.test_timeseries import datetime_of


def simple_gpx_file(entry):
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    gpx_segment.points.append(
        gpxpy.gpx.GPXTrackPoint(
            time=entry.dt,
            latitude=entry.point.lat,
            longitude=entry.point.lon,
            elevation=entry.alt.to("m").magnitude)
    )

    return gpx.to_xml()


def test_loading_a_simple_gpx_file():
    entry = Entry(
        dt=datetime_of(0),
        point=Point(lat=1.23, lon=4.56),
        alt=units.Quantity(23, units.m)
    )

    xml = simple_gpx_file(entry)

    entries = list(gpx.load_xml(xml, units))

    assert len(entries) == 1
    assert entries[0].lat == 1.23
    assert entries[0].lon == 4.56
    assert entries[0].hr is None


def test_bugfix_20_gpsbabel_converted():
    xml = """<gpx 
    xmlns="http://www.topografix.com/GPX/1/1" 
    xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" 
    version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="34.405176993" lon="-119.842140907">
        <ele>-4.000</ele>
        <time>2022-02-15T22:12:27Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:atemp>20.000000</gpxtpx:atemp>
            <gpxtpx:hr>153</gpxtpx:hr>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""

    entries = list(gpx.load_xml(xml, units))

    assert len(entries) == 1
    assert entries[0].lat == 34.405176993
    assert entries[0].lon == -119.842140907
    assert entries[0].hr.magnitude == 153
    assert entries[0].atemp.magnitude == 20
