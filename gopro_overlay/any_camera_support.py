import os

from datetime import datetime, timedelta, timezone

from .dimensions import Dimension, dimension_from
from .entry import Entry
from .ffmpeg import StreamInfo, VideoMeta, find_streams
from .framemeta import FrameMeta
from .gpx import load_timeseries
from .timeunits import timeunits

def video_from_gopro_camera(args):
    return not (args.gpx and ((args.input == "-" and args.generate == "overlay") or (args.video_time_start or args.video_time_end)))

# we are parsing gpx file multiple times (3 times), for sure this could be improved but I think that this is not a performance problem right now

def emulate_streams(args, units) -> StreamInfo:
    if args.input != "-":
        return find_streams(args.input, skip_meta=True)

    gpx_timeseries = load_timeseries(args.gpx, units)
    start = gpx_timeseries.min
    end = gpx_timeseries.max

    video_meta = VideoMeta(
        stream=None,
        dimension=dimension_from(args.overlay_size or "1920x1080"),
        duration=timeunits(micros=(end - start) / timedelta(microseconds=1))
    )

    return StreamInfo(audio=None, video=video_meta, meta=None)

def emulate_frame_meta(args, stream_info: StreamInfo, units) -> FrameMeta:
    result = FrameMeta()
    if args.input == "-":
        gpx_timeseries = load_timeseries(args.gpx, units)
        start = gpx_timeseries.min
    else:
        start = datetime.fromtimestamp(getattr(os.path, "get" + (args.video_time_start or args.video_time_end))(args.input)).astimezone()
        if args.video_time_end:
            start = start - timedelta(milliseconds=stream_info.video.duration.millis())
    for offset in range(0, int(stream_info.video.duration.millis()), 100):
        dt = start + timedelta(milliseconds=offset)
        point = Entry(dt, timestamp=units.Quantity(offset, units.number))
        result.add(timeunits(millis=offset), point)

    return result
