#!/usr/bin/env python3

import argparse
import os.path
import pathlib

from gopro_overlay.ffmpeg import join_files
from gopro_overlay.filenaming import GoProFile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate sequence of GoPro Files")

    parser.add_argument("input", type=pathlib.Path, help="A single MP4 file from the sequence")
    parser.add_argument("output", type=pathlib.Path, help="Output MP4 file")

    args = parser.parse_args()

    source: pathlib.Path = args.input

    if not source.exists():
        raise IOError(f"File not found {source}")

    directory = source.parent.absolute()

    file = GoProFile(source)

    found = file.related_files(directory)

    print(f"Found: {[f.name for f in found]}")

    if not found:
        print("Didn't find any suitable files to join. Were the files renamed?")
        exit(1)

    join_files(
        filepaths=[os.path.join(directory, file.name) for file in found],
        output=args.output
    )
