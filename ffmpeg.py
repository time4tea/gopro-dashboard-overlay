import re
import subprocess
from array import array


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def invoke(cmd, **kwargs):
    try:
        return run(cmd, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="UTF-8")
    except subprocess.CalledProcessError as e:
        raise IOError(f"Failed: {cmd}\n Stdout: {e.stdout}\n StdErr: {e.stderr}")


def find_gpmd_track(filepath):
    ffprobe_output = str(invoke(["ffprobe", filepath]).stderr)  # str here just for PyCharm - its already a string

    # look for: Stream #0:3(eng): Data: bin_data (gpmd / 0x646D7067), 61 kb/s (default)
    match = re.search('Stream #\d:(\d)\(.+\): Data: \w+ \(gpmd', ffprobe_output)
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


if __name__ == "__main__":
    loaded = load_gpmd_from("/data/richja/gopro/GH010064.MP4")
    print(len(loaded))
