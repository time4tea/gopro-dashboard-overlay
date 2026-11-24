import subprocess


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def invoke(cmd, **kwargs):
    try:
        return run(cmd, **kwargs, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        if "moov atom not found" in (e.stderr or ""):
            raise IOError(
                "The file has no moov atom (its index): the recording was probably interrupted before it was "
                "written, for example because the battery died or the card was removed. "
                f"The video data may still be in the file.\n {cmd}\n stderr: {e.stderr}"
            )
        raise IOError(f"Error: {cmd}\n stdout: {e.stdout}\n stderr: {e.stderr}")
