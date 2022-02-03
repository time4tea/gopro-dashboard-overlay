#!/usr/bin/env python3

import argparse
import os.path

from gopro_overlay.ffmpeg import cut_file
from gopro_overlay.parsing import parse_time


def as_seconds(timey):
    parsed_time = parse_time(timey)
    return (parsed_time.hour * 3600) + (parsed_time.minute * 60) + parsed_time.second + (
            parsed_time.microsecond / 100000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract section of GoPro Files")

    parser.add_argument("input", help="A single MP4 file ")

    parser.add_argument("--start", help="Time to start (hh:mm:ss.SSSSSS)")
    parser.add_argument("--end", help="Time to end (hh:mm:ss.SSSSSS)")
    parser.add_argument("--duration", help="Duration of clip (hh:mm:ss.SSSSSS)")

    parser.add_argument("output", help="Output MP4 file")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise IOError(f"File not found {args.input}")

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

    cut_file(args.input, args.output, from_seconds, duration)
