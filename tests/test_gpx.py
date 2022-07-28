import inspect
import os
from pathlib import Path

import gpxpy

from gopro_overlay import gpx, framemeta
from gopro_overlay.ffmpeg import MetaMeta
from gopro_overlay.framemeta_gpx import merge_gpx_with_gopro
from gopro_overlay.journey import Journey
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


def file_path_of_test_asset(name, in_dir="gpx"):
    sourcefile = Path(inspect.getfile(file_path_of_test_asset))

    meta_dir = sourcefile.parents[0].joinpath(in_dir)

    the_path = os.path.join(meta_dir, name)

    if not os.path.exists(the_path):
        raise IOError(f"Test file {the_path} does not exist")

    return the_path


def test_loading_gpx_file():
    gpx.load(file_path_of_test_asset("test.gpx.gz"), units)


def test_converting_gpx_to_timeseries():
    ts = gpx.load_timeseries(file_path_of_test_asset("test.gpx.gz"), units)

    assert len(ts) == 8597

    first = ts.items()[0]

    assert first.point == Point(lat=51.339589, lon=-2.572136)
    assert first.alt == units.Quantity(96.0, units.m)
    assert first.hr == units.Quantity(66, units.bpm)
    assert first.atemp == units.Quantity(16, units.celsius)
    assert first.gpsfix == 3


def test_bugfix_converting_gpx_to_journey():
    ts = gpx.load_timeseries(file_path_of_test_asset("test.gpx.gz"), units)

    journey = Journey()
    ts.process(journey.accept)

    assert journey.bounding_box == (Point(lat=51.184804, lon=-2.804645), Point(lat=51.342323, lon=-2.571981))
    assert len(journey.locations) == 8597

def test_merge_gpx_with_gopro():
    # the two files should be of the same trip
    gpx_timeseries = gpx.load_timeseries(file_path_of_test_asset("test.gpx.gz"), units)
    gopro_framemeta = framemeta.framemeta_from_datafile(
        file_path_of_test_asset("gopro-meta.gpmd", in_dir="meta"),
        units,
        metameta=MetaMeta(stream=3, frame_count=707, timebase=1000, frame_duration=1001)
    )
    assert gpx_timeseries.min < gopro_framemeta.get(gopro_framemeta.min).dt
    assert gpx_timeseries.max > gopro_framemeta.get(gopro_framemeta.max).dt

    merge_gpx_with_gopro(gpx_timeseries, gopro_framemeta)
