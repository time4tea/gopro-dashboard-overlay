import contextlib
import re
import subprocess
import sys
from array import array
from collections import namedtuple


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def invoke(cmd, **kwargs):
    try:
        return run(cmd, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="UTF-8")
    except subprocess.CalledProcessError as e:
        raise IOError(f"Error: {cmd}\n stdout: {e.stdout}\n stderr: {e.stderr}")


StreamInfo = namedtuple("StreamInfo", ["audio", "video", "meta"])


def find_streams(filepath, invoke=invoke):
    ffprobe_output = str(invoke(["ffprobe", "-hide_banner", filepath]).stderr)

    video_re = re.compile(r"Stream #\d+:(\d+)\(.+\): Video")
    audio_re = re.compile(r"Stream #\d+:(\d+)\(.+\): Audio")
    meta_re = re.compile(r"Stream #\d+:(\d+)\(.+\): Data: bin_data \(gpmd")

    video_stream = None
    audio_stream = None
    meta_stream = None

    for line in ffprobe_output.split("\n"):
        video_match = video_re.search(line)
        if video_match:
            video_stream = int(video_match.group(1))
        audio_match = audio_re.search(line)
        if audio_match:
            audio_stream = int(audio_match.group(1))
        meta_match = meta_re.search(line)
        if meta_match:
            meta_stream = int(meta_match.group(1))

    if video_stream is None or audio_stream is None or meta_stream is None:
        raise IOError("Invalid File? The data stream doesn't seem to contain GoPro audio, video & metadata ")

    return StreamInfo(audio_stream, video_stream,  meta_stream)


def load_gpmd_from(filepath):
    track = find_streams(filepath).meta
    if track:
        cmd = ["ffmpeg", '-y', '-i', filepath, '-codec', 'copy', '-map', '0:%d' % track, '-f', 'rawvideo', "-"]
        result = run(cmd, capture_output=True, timeout=10)
        if result.returncode != 0:
            raise IOError(f"ffmpeg failed code: {result.returncode} : {result.stderr.decode('utf-8')}")
        arr = array("b")
        arr.frombytes(result.stdout)
        return arr


def ffmpeg_is_installed():
    try:
        invoke(["ffmpeg", "-version"])
        return True
    except FileNotFoundError:
        return False


def ffmpeg_libx264_is_installed():
    output = invoke(["ffmpeg", "-v", "quiet", "-codecs"]).stdout
    libx264s = [x for x in output.split('\n') if "libx264" in x]
    return len(libx264s) > 0


class FFMPEGGenerate:

    def __init__(self, output):
        self.output = output

    @contextlib.contextmanager
    def generate(self):
        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel", "info",
            "-f", "rawvideo",
            "-framerate", "10.0",
            "-s", "1920x1080",
            "-pix_fmt", "rgba",
            "-i", "-",
            "-r", "30",
            "-vcodec", "libx264",
            "-preset", "veryfast",
            self.output
        ]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=None, stderr=None)
        yield process.stdin
        process.stdin.close()
        process.wait(10)


class FFMPEGOverlay:

    def __init__(self, input, output, vsize=1080, redirect=None):
        self.output = output
        self.input = input
        self.vsize = vsize
        self.redirect = redirect

    @contextlib.contextmanager
    def generate(self):
        if self.vsize == 1080:
            filter_extra = ""
        else:
            filter_extra = f",scale=-1:{self.vsize}"
        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel", "info",
            "-i", self.input,
            "-f", "rawvideo",
            "-framerate", "10.0",
            "-s", "1920x1080",
            "-pix_fmt", "rgba",
            "-i", "-",
            "-r", "30",
            "-filter_complex", f"[0:v][1:v]overlay{filter_extra}",
            "-vcodec", "libx264",
            "-preset", "veryfast",
            self.output
        ]

        try:
            if self.redirect:
                with open(self.redirect, "w") as std:
                    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=std, stderr=std)
            else:
                process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=None, stderr=None)

            yield process.stdin
            process.stdin.close()
            # really long wait as FFMPEG processes all the mpeg input file - not sure how to prevent this atm
            process.wait(5 * 60)
        except FileNotFoundError:
            raise IOError("Unable to start the 'ffmpeg' process - is FFMPEG installed?") from None
        except BrokenPipeError:
            if self.redirect:
                print("FFMPEG Output:")
                with open(self.redirect) as f:
                    print("".join(f.readlines()), file=sys.stderr)
            raise IOError("FFMPEG reported an error - can't continue") from None


if __name__ == "__main__":
    print(ffmpeg_libx264_is_installed())
