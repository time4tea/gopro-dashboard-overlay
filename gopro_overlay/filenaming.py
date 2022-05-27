import os
import re
from enum import Enum
from pathlib import Path


# https://community.gopro.com/t5/en/GoPro-Camera-File-Naming-Convention/ta-p/390220
from typing import List


class Encoding(Enum):
    AVC = 1
    HEVC = 2

    @staticmethod
    def from_letter(letter):
        if letter == "H":
            return Encoding.AVC
        elif letter == "X":
            return Encoding.HEVC
        else:
            raise ValueError(f"Unknown encoding letter {letter}")


def gopro_files_in(path) -> List[Path]:
    path = Path(path)
    if path.is_file():
        if GoProFile.is_valid_filename(path.name):
            return [path]
    elif path.is_dir():
        return [Path(path) / f for f in os.listdir(path) if GoProFile.is_valid_filename(f)]
    else:
        raise ValueError(f"{path} is not file or directory?")


class GoProFile:

    def __init__(self, filename):
        match = GoProFile.is_valid_filename(filename)
        if match is None:
            raise ValueError(f"Not a GoPro file {filename}")

        self.name = filename
        self.encoding = Encoding.from_letter(match.group(1))
        self.letter = match.group(1)
        self.recording = int(match.group(3))
        self.sequence = int(match.group(2))

    @staticmethod
    def is_valid_filename(filename):
        return re.search(r"G([HX])(\d{2})(\d{4}).MP4", filename)

    def related_files(self, directory, listdir=os.listdir):
        find = re.compile(r"G{l}\d\d{n}\.MP4".format(
            l=self.letter,
            n=f"{self.recording:04}"
        ))
        found = [GoProFile(name) for name in listdir(directory) if find.match(name)]
        found.sort(key=lambda f: f.sequence)
        return found
