import contextlib
import re
import subprocess
from array import array


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def invoke(cmd, **kwargs):
    try:
        return run(cmd, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="UTF-8")
    except subprocess.CalledProcessError as e:
        raise IOError(f"Error: {cmd}\n stdout: {e.stdout}\n stderr: {e.stderr}")


def find_gpmd_track(filepath):
    ffprobe_output = str(invoke(["ffprobe", filepath]).stderr)  # str here just for PyCharm - its already a string

    # look for: Stream #0:3(eng): Data: bin_data (gpmd / 0x646D7067), 61 kb/s (default)
    match = re.search(r'Stream #\d:(\d)\(.+\): Data: \w+ \(gpmd', ffprobe_output)
    if match:
        return int(match.group(1))


def load_gpmd_from(filepath):
    track = find_gpmd_track(filepath)
    if track:
        cmd = ["ffmpeg", '-y', '-i', filepath, '-codec', 'copy', '-map', '0:%d' % track, '-f', 'rawvideo', "-"]
        result = run(cmd, capture_output=True, timeout=10)
        if result.returncode != 0:
            raise IOError(f"ffmpeg failed code: {result.returncode} : {result.stderr.decode('utf-8')}")
        arr = array("b")
        arr.frombytes(result.stdout)
        return arr


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
            "-crf", "18",
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
            f"-filter_complex", f"[0:v][1:v]overlay{filter_extra}",
            "-vcodec", "libx264",
            "-crf", "18",
            "-preset", "veryfast",
            self.output
        ]

        if self.redirect:
            with open(self.redirect, "w") as std:
                process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=std, stderr=std)
        else:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=None, stderr=None)

        yield process.stdin
        process.stdin.close()
        # really long wait as FFMPEG processes all the mpeg input file - not sure how to prevent this atm
        process.wait(5 * 60)


if __name__ == "__main__":
    loaded = load_gpmd_from("/data/richja/gopro/GH010064.MP4")
    print(len(loaded))
