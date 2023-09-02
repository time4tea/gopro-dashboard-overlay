#!/usr/bin/env python3

import argparse
import pathlib

from gopro_overlay.assertion import assert_file_exists
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro
from gopro_overlay.parsing import parse_time


def as_seconds(timey):
    parsed_time = parse_time(timey)
    return (parsed_time.hour * 3600) + (parsed_time.minute * 60) + parsed_time.second + (
            parsed_time.microsecond / 100000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract section of GoPro Files")

    parser.add_argument("input", type=pathlib.Path, help="A single MP4 file ")
    parser.add_argument("--ffmpeg-dir", type=pathlib.Path,
                        help="Directory where ffmpeg/ffprobe located, default=Look in PATH")

    parser.add_argument("--start", help="Time to start (hh:mm:ss.SSSSSS)")
    parser.add_argument("--end", help="Time to end (hh:mm:ss.SSSSSS)")
    parser.add_argument("--duration", help="Duration of clip (hh:mm:ss.SSSSSS)")

    parser.add_argument("output", type=pathlib.Path, help="Output MP4 file")

    args = parser.parse_args()

    from_seconds = as_seconds(args.start)
    duration = None

    if args.end:
        to_seconds = as_seconds(args.end)
        duration = to_seconds - from_seconds

        if duration < 0:
            raise ValueError("End should be after start")

    elif args.duration:
        duration = as_seconds(args.duration)
    else:
        parser.print_help()
        exit(1)

    if duration == 0:
        raise ValueError("Duration should be more than zero")

    ffmpeg_gopro = FFMPEGGoPro(FFMPEG(args.ffmpeg_dir))

    ffmpeg_gopro.cut_file(
        assert_file_exists(args.input),
        args.output,
        from_seconds,
        duration
    )
