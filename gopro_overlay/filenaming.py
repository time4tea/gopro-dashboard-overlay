
# https://community.gopro.com/t5/en/GoPro-Camera-File-Naming-Convention/ta-p/390220
import os
import re
from enum import Enum


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


class GoProFile:

    def __init__(self, filename):
        match = re.search(r"G([HX])(\d{2})(\d{4}).MP4", filename)
        if match is None:
            raise ValueError(f"Not a GoPro file {filename}")
        self.name = filename
        self.encoding = Encoding.from_letter(match.group(1))
        self.letter = match.group(1)
        self.recording = int(match.group(3))
        self.sequence = int(match.group(2))

    def related_files(self, directory, listdir=os.listdir):
        find = re.compile(r"G{l}\d\d{n}\.MP4".format(
            l=self.letter,
            n=f"{self.recording:04}"
        ))
        found = [GoProFile(name) for name in listdir(directory) if find.match(name)]
        found.sort(key=lambda f: f.sequence)
        return found

