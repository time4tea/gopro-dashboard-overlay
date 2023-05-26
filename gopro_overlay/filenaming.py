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
        if letter == "H" or letter == "P" or letter == "OPR":
            return Encoding.AVC
        elif letter == "X":
            return Encoding.HEVC
        else:
            raise ValueError(f"Unknown encoding letter {letter}")


def gopro_files_in(path:Path) -> List[Path]:
    path = Path(path)
    if path.is_file():
        if GoProFile.is_valid_filepath(path):
            return [path]
    elif path.is_dir():
        potentials = [ path / f for f in os.listdir(path) ]
        return [p for p in potentials if GoProFile.is_valid_filepath(p)]
    else:
        raise ValueError(f"{path} is not file or directory?")


class GoProFile:

    def __init__(self, filepath: Path):
        match = GoProFile.is_valid_filepath(filepath)
        if match is None:
            raise ValueError(f"Not a valid GoPro filename {filepath}")

        self.name = filepath.name
        self.encoding = Encoding.from_letter(match.group(1))
        self.letter = match.group(1)
        self.recording = int(match.group(3))
        self.sequence = int(match.group(2)) if match.group(2) is not None else 0
        self.extension = match.group(4)

    @staticmethod
    def is_valid_filepath(f: Path):
        return re.search(r"^G([HXP]|OPR)(\d{2})?(\d{4}).(MP4|mp4)", f.name)

    def related_files(self, d: Path, listdir=os.listdir):
        find = re.compile(r"G{l}\d\d{n}\.{e}".format(
            l=self.letter,
            e=self.extension,
            n=f"{self.recording:04}"
        ))

        potentials = [ d / name for name in listdir(d) ]

        found = [GoProFile(p) for p in potentials if find.match(p.name)]
        found.sort(key=lambda f: f.sequence)
        return found
