import inspect
from pathlib import Path

import gpxpy

from gopro_overlay import gpx, framemeta
from gopro_overlay.ffmpeg_gopro import DataStream
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.framemeta_gpx import merge_gpx_with_gopro, timeseries_to_framemeta, MergeMode
from gopro_overlay.gpmf import GPSFix
from gopro_overlay.gpx import gpx_to_timeseries
from gopro_overlay.journey import Journey
from gopro_overlay.point import Point, BoundingBox
from gopro_overlay.timeseries import Entry, Timeseries
from gopro_overlay.timeunits import timeunits
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
    entry = entries[0]
    assert entry.lat == 1.23
    assert entry.lon == 4.56
    assert entry.alt.m == 23
    assert entry.hr is None


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


def test_feature_70_power_converted():
    xml = """<gpx 
    xmlns="http://www.topografix.com/GPX/1/1" 
    xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" 
    version="1.1">
  <trk>
    <trkseg>
         <trkpt lat="55.2359580" lon="10.4869030">
        <ele>78.8</ele>
        <time>2022-07-09T07:09:31Z</time>
        <extensions>
         <power>103</power>
         <gpxtpx:TrackPointExtension>
          <gpxtpx:atemp>21</gpxtpx:atemp>
          <gpxtpx:hr>113</gpxtpx:hr>
          <gpxtpx:cad>96</gpxtpx:cad>
         </gpxtpx:TrackPointExtension>
        </extensions>
   </trkpt>
    </trkseg>
  </trk>
</gpx>"""

    entries = list(gpx.load_xml(xml, units))

    assert len(entries) == 1
    assert entries[0].power == units.Quantity(103, units.W)


def test_discussion_85_speed_elevation_from_gpx():
    xml = """
    <gpx 
    xmlns="http://www.topografix.com/GPX/1/1" 
    xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" 
    version="1.1">
  <trk>
   <trkseg>
    <trkpt lat="38.900207" lon="-77.008990">
    <ele>11.67</ele>
    <time>2013-06-11T04:04:49Z</time>
    <extensions>
      <gpxtpx:TrackPointExtension>
        <gpxtpx:speed>6.86</gpxtpx:speed> 
      </gpxtpx:TrackPointExtension>
    </extensions>
    </trkpt>
    <trkpt lat ="47.37736003508461" lon ="8.539389877469207">
        <ele>444.746359774318</ele>
        <time>2022-05-26T17:34:49Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
           <gpxtpx:speed>3.77</gpxtpx:speed>
          </gpxtpx:TrackPointExtension>
        </extensions>
        </trkpt>
            <trkpt lat ="47.37736003508461" lon ="8.539389877469207">
        <ele>444.746359774318</ele>
        <time>2022-05-26T17:34:49Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
           <gpxtpx:speed>0.0</gpxtpx:speed>
          </gpxtpx:TrackPointExtension>
        </extensions>
        </trkpt>
    </trkseg>
  </trk>
</gpx>
    """

    entries = list(gpx.load_xml(xml, units))
    assert len(entries) == 3
    assert entries[0].alt == units.Quantity(11.67, units.m)
    assert entries[0].speed == units.Quantity(6.86, units.mps)
    assert entries[1].speed == units.Quantity(3.77, units.mps)
    assert entries[2].speed == units.Quantity(0.0, units.mps)


def file_path_of_test_asset(name, in_dir="gpx") -> Path:
    sourcefile = Path(inspect.getfile(file_path_of_test_asset))

    meta_dir = sourcefile.parents[0].joinpath(in_dir)

    the_path = Path(meta_dir) / name

    if not the_path.exists():
        raise IOError(f"Test file {the_path} does not exist")

    return the_path


def test_loading_gpx_file():
    gpx.load(file_path_of_test_asset("test.gpx.gz"), units)


def test_converting_gpx_item_to_timeseries():
    dt = datetime_of(0)
    xml = simple_gpx_file(Entry(dt=dt, point=Point(lat=1, lon=2), alt=units.Quantity(1, units.m)))
    ts = gpx_to_timeseries(gpx.load_xml(xml, units), units)
    assert len(ts) == 1
    assert ts.get(dt).gpsfix == GPSFix.LOCK_3D.value
    assert ts.get(dt).gpslock.m == GPSFix.LOCK_3D.value
    assert ts.get(dt).packet.m == 0
    assert ts.get(dt).packet_index.m == 0


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

    assert journey.bounding_box == BoundingBox(Point(lat=51.184804, lon=-2.804645), Point(lat=51.342323, lon=-2.571981))
    assert len(journey.locations) == 8597


def test_merge_gpx_with_gopro():
    # the two files should be of the same trip
    gpx_timeseries = gpx.load_timeseries(file_path_of_test_asset("test.gpx.gz"), units)
    gopro_framemeta = framemeta.framemeta_from_datafile(
        file_path_of_test_asset("gopro-meta.gpmd", in_dir="meta"),
        units,
        datastream=DataStream(stream=3, frame_count=707, timebase=1000, frame_duration=1001),
        flags=set()
    )

    assert gpx_timeseries.min < gopro_framemeta.get(gopro_framemeta.min).dt
    assert gpx_timeseries.max > gopro_framemeta.get(gopro_framemeta.max).dt

    assert gopro_framemeta[0].alt == units.Quantity(171.843, units.m)
    assert gopro_framemeta[0].hr is None
    first_point = gopro_framemeta[0].point

    merge_gpx_with_gopro(gpx_timeseries, gopro_framemeta)

    assert gopro_framemeta[0].point != first_point                # point replaced
    assert gopro_framemeta[0].alt == units.Quantity(160.2104, units.m)  # alt replaced
    assert gopro_framemeta[0].hr == units.Quantity(103.0, units.bpm) # hr added


def test_merge_gpx_with_gopro_extend_mode():
    # the two files should be of the same trip
    gpx_timeseries = gpx.load_timeseries(file_path_of_test_asset("test.gpx.gz"), units)
    gopro_framemeta = framemeta.framemeta_from_datafile(
        file_path_of_test_asset("gopro-meta.gpmd", in_dir="meta"),
        units,
        datastream=DataStream(stream=3, frame_count=707, timebase=1000, frame_duration=1001),
        flags=set()
    )
    assert gpx_timeseries.min < gopro_framemeta.get(gopro_framemeta.min).dt
    assert gpx_timeseries.max > gopro_framemeta.get(gopro_framemeta.max).dt

    assert gopro_framemeta[0].alt == units.Quantity(171.843, units.m)
    assert gopro_framemeta[0].hr is None
    first_point = gopro_framemeta[0].point

    merge_gpx_with_gopro(gpx_timeseries, gopro_framemeta, mode=MergeMode.EXTEND)

    assert gopro_framemeta[0].point == first_point                        # point remains
    assert gopro_framemeta[0].alt == units.Quantity(171.843, units.m)     # alt remains
    assert gopro_framemeta[0].hr == units.Quantity(103.0, units.bpm)      # hr added


def test_merge_gpx_with_gopro_gpx_gps_location_and_speed_takes_priority():
    dt = datetime_of(1)

    gopro_data = FrameMeta()
    t = timeunits(seconds=0)
    gopro_data.add(t, Entry(dt=dt, point=Point(lat=1, lon=1), speed=units.Quantity(1, units.mps)))

    gpx_data = Timeseries()
    gpx_data.add(Entry(dt=dt, point=Point(lat=2, lon=2), speed=units.Quantity(2, units.mps)))

    merge_gpx_with_gopro(gpx_data, gopro_data)

    assert gopro_data.get(t).dt == dt
    assert gopro_data.get(t).point == Point(lat=2, lon=2)
    assert gopro_data.get(t).speed == units.Quantity(2, units.mps)


def test_merge_gpx_with_gopro_gpx_dop_and_gpsfix_are_corrected():
    dt = datetime_of(1)

    gopro_data = FrameMeta()
    t = timeunits(seconds=0)
    gopro_data.add(t, Entry(dt=dt, dop=units.Quantity(99), gpsfix=GPSFix.UNKNOWN.value))

    gpx_data = Timeseries()
    gpx_data.add(Entry(dt=dt, gpsfix=GPSFix.LOCK_3D.value))

    merge_gpx_with_gopro(gpx_data, gopro_data)

    assert len(gopro_data) == 1
    assert gopro_data.get(t).dt == dt
    assert gopro_data.get(t).dop is None
    assert gopro_data.get(t).gpsfix == GPSFix.LOCK_3D.value


def test_merge_gpx_with_gopro_speed_is_removed_if_not_present_in_gpx():
    dt = datetime_of(1)

    gopro_data = FrameMeta()
    t = timeunits(seconds=0)
    gopro_data.add(t, Entry(dt=dt, speed=units.Quantity(1, units.mps)))

    gpx_data = Timeseries()
    gpx_data.add(Entry(dt=dt))

    merge_gpx_with_gopro(gpx_data, gopro_data)

    assert gopro_data.get(t).dt == dt
    assert gopro_data.get(t).speed is None


def test_converting_gpx_to_timeseries_to_framemeta():
    gpx_timeseries = gpx.load_timeseries(file_path_of_test_asset("test.gpx.gz"), units)

    gpx_framemeta = timeseries_to_framemeta(gpx_timeseries, units)

    ts_len = len(gpx_timeseries)
    fm_len = len(gpx_framemeta)

    assert fm_len > 11 * ts_len

def test_converting_fit_without_dop_to_framemeta():
    ts = Timeseries()
    ts.add(Entry(
        dt=datetime_of(1),
    ))

    fm = timeseries_to_framemeta(ts, units)

    assert fm.frames[timeunits(seconds=0)].dop == units.Quantity(10)


def test_converting_fit_with_dop_to_framemeta():
    ts = Timeseries()
    ts.add(Entry(
        dt=datetime_of(1),
        dop=units.Quantity(1)
    ))

    fm = timeseries_to_framemeta(ts, units)

    assert fm.frames[timeunits(seconds=0)].dop == units.Quantity(1)

