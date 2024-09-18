from __future__ import annotations

import datetime
import itertools
import json
import os
import pathlib
import subprocess
from array import array
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from gopro_overlay.common import temporary_file
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.progresstrack import ProgressBarProgress
from gopro_overlay.timeunits import timeunits, Timeunit


class FFMPEGGoPro:

    def __init__(self, exe: FFMPEG):
        self.exe = exe

    def join_files(self, filepaths, output):
        """only for joining parts of same trip"""

        streams = self.find_recording(filepaths[0])

        maps = list(itertools.chain.from_iterable(
            [["-map", f"0:{it.stream}"] for it in [streams.video, streams.audio, streams.data] if it is not None]))

        with temporary_file() as commandfile:
            with open(commandfile, "w") as f:
                for path in filepaths:
                    f.write(f"file '{path}\n")

            self.exe.run(
                ["-hide_banner",
                 "-y",
                 "-f", "concat",
                 "-safe", "0",
                 "-i", commandfile,
                 "-map_metadata", "0",
                 *maps,
                 "-copy_unknown",
                 "-c", "copy",
                 output]
            )

    def find_frame_duration(self, filepath, data_stream_number):
        ffprobe_output = str(self.exe.ffprobe().invoke(
            ["-hide_banner",
             "-print_format", "json",
             "-show_packets",
             "-select_streams", str(data_stream_number),
             "-read_intervals", "%+#1",
             filepath]
        ).stdout)

        ffprobe_packet_data = json.loads(ffprobe_output)
        packet = ffprobe_packet_data["packets"][0]

        duration = int(packet["duration"])

        return duration

    def find_recording(self, filepath: Path, stat=os.stat) -> GoproRecording:
        ffprobe_output = str(self.exe.ffprobe().invoke(
            [
                "-hide_banner",
                "-print_format", "json",
                "-show_streams",
                "-show_entries", "stream_tags:format_tags",
                filepath
            ]
        ).stdout)

        ffprobe_json = json.loads(ffprobe_output)

        video_selector = lambda s: s["codec_type"] == "video"
        audio_selector = lambda s: s["codec_type"] == "audio"
        data_selector = lambda s: s["codec_type"] == "data" and s["codec_tag_string"] == "gpmd"

        def first_and_only(what, l, p):
            matches = list(filter(p, l))
            if not matches:
                raise IOError(f"Unable to find {what} in ffprobe output")
            if len(matches) > 1:
                raise IOError(f"Multiple matching streams for {what} in ffprobe output")
            return matches[0]

        def only_if_present(what, l, p):
            matches = list(filter(p, l))
            if matches:
                return first_and_only(what, l, p)

        streams = ffprobe_json["streams"]
        video = first_and_only("video stream", streams, video_selector)

        avg_frame_rate_fraction = video["avg_frame_rate"].split("/")
        video_stream = VideoStream(
            stream=int(video["index"]),
            dimension=Dimension(video["width"], video["height"]),
            duration=timeunits(seconds=float(video["duration"])),
            frame_count=int(video["nb_frames"]),
            frame_rate_numerator=int(avg_frame_rate_fraction[0]),
            frame_rate_denominator=int(avg_frame_rate_fraction[1]),
        )

        audio = only_if_present("audio stream", streams, audio_selector)
        audio_stream = None
        if audio:
            audio_stream = AudioStream(stream=int(audio["index"]))

        data = only_if_present("metadata stream", streams, data_selector)

        if data:
            data_stream_number = int(data["index"])

            data_stream = DataStream(
                stream=data_stream_number,
                frame_count=int(data["nb_frames"]),
                timebase=int(data["time_base"].split("/")[1]),
                frame_duration=self.find_frame_duration(filepath, data_stream_number)
            )
        else:
            data_stream = None

        creationDateTime = None
        try:
            creationDateTime = datetime.datetime.fromisoformat(ffprobe_json["format"]["tags"]["creation_time"])
        except Exception:
            pass

        return GoproRecording(
            ffmpeg=self.exe,
            location=filepath,
            file=filestat(filepath, stat=stat),
            audio=audio_stream,
            video=video_stream,
            data=data_stream,
            creationDateTime=creationDateTime
        )

    def load_frame(self, filepath: Path, at_time: Timeunit) -> Optional[bytes]:
        if filepath.exists():
            cmd = ["-hide_banner",
                   "-y",
                   "-ss", str(at_time.millis() / 1000),
                   "-i", str(filepath.absolute()),
                   "-frames:v", "1",
                   "-f", "rawvideo",
                   "-pix_fmt", "rgba",
                   "-"
                   ]
            try:
                return self.exe.run(cmd, capture_output=True).stdout
            except subprocess.CalledProcessError as e:
                raise IOError(f"Error: {cmd}\n stderr: {e.stderr}")

    def cut_file(self, input: pathlib.Path, output, start, duration):
        streams = self.find_recording(input)

        maps = list(itertools.chain.from_iterable(
            [["-map", f"0:{it.stream}"] for it in [streams.video, streams.audio, streams.data] if it is not None]))

        args = [
            "-hide_banner",
            "-y",
            "-i", input,
            "-map_metadata", "0",
            *maps,
            "-copy_unknown",
            "-ss", str(start),
            "-t", str(duration),
            "-c", "copy",
            output
        ]

        self.exe.run(args)


@dataclass(frozen=True)
class FileStat:
    length: int
    mtime: datetime.datetime
    ctime: datetime.datetime
    atime: datetime.datetime


def filestat(filepath: Path, stat=os.stat) -> FileStat:
    sr = stat(filepath)

    return FileStat(
        length=sr.st_size,
        ctime=datetime.datetime.fromtimestamp(sr.st_ctime, tz=datetime.timezone.utc),
        atime=datetime.datetime.fromtimestamp(sr.st_atime, tz=datetime.timezone.utc),
        mtime=datetime.datetime.fromtimestamp(sr.st_mtime, tz=datetime.timezone.utc)
    )


@dataclass(frozen=True)
class GoproRecording:
    ffmpeg: FFMPEG
    location: Path
    file: FileStat
    audio: Optional[AudioStream]
    video: VideoStream
    data: Optional[DataStream]
    creationDateTime: datetime.datetime

    def load_data(self) -> bytes:
        track = self.data.stream
        if track:
            cmd = [
                "-hide_banner",
                '-y',
                '-i', self.location,
                '-codec', 'copy',
                '-map', '0:%d' % track,
                '-f', 'rawvideo',
                "-"
            ]

            progress = ProgressBarProgress("Loading GoPro Data Track", transfer=True, delta=True)
            progress.start()
            try:
                arr = bytearray()

                def update(b: bytes):
                    progress.update(len(b))
                    arr.extend(b)

                result = self.ffmpeg.stream(cmd, cb=update, timeout=datetime.timedelta(seconds=45))
                if result != 0:
                    raise IOError(f"ffmpeg failed code: {result}")
                return bytes(arr)
            finally:
                progress.complete()


@dataclass(frozen=True)
class DataStream:
    stream: int
    frame_count: int
    timebase: int
    frame_duration: int


@dataclass(frozen=True)
class VideoStream:
    stream: int
    dimension: Dimension
    duration: Timeunit
    frame_count: int
    frame_rate_numerator: int
    frame_rate_denominator: int

    def frame_rate(self) -> float:
        return self.frame_rate_numerator / self.frame_rate_denominator


@dataclass(frozen=True)
class AudioStream:
    stream: int
