import sys

import pytest

from gopro_overlay.process import invoke


def test_interrupted_recording_is_reported():
    # What ffprobe prints for a recording cut off before its moov atom was written
    fake_ffprobe = [
        sys.executable, "-c",
        "import sys; sys.stderr.write('[mov,mp4,m4a,3gp,3g2,mj2] moov atom not found\n'); sys.exit(1)",
    ]
    with pytest.raises(IOError, match="recording was probably interrupted"):
        invoke(fake_ffprobe)


def test_other_failures_keep_the_generic_error():
    with pytest.raises(IOError, match="^Error: "):
        invoke([sys.executable, "-c", "import sys; sys.exit(1)"])
