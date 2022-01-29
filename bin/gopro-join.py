#!/usr/bin/env python3

import argparse
import os.path

from gopro_overlay.ffmpeg import join_files
from gopro_overlay.filenaming import GoProFile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate sequence of GoPro Files")

    parser.add_argument("input", help="A single MP4 file from the sequence")
    parser.add_argument("output", help="Output MP4 file")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise IOError(f"File not found {args.input}")

    directory = os.path.dirname(args.input)
    filename = os.path.basename(args.input)

    file = GoProFile(filename)

    found = file.related_files(directory)

    print(f"Found: {[f.name for f in found]}")

    join_files(
        filepaths=[os.path.join(directory, file.name) for file in found],
        output=args.output
    )
