import json
import tempfile
from pathlib import Path

from gopro_overlay.config import Config
from gopro_overlay.ffmpeg_profile import load_ffmpeg_profile

simple = {
    "simple": {
        "input": ["i1", "i2"],
        "output": ["o1", "o2"]
    }
}


def test_loading_a_profile():
    with tempfile.TemporaryDirectory() as tempdir:
        config = Path(tempdir) / "ffmpeg-profiles.json"
        config.write_text(json.dumps(simple))

        loader = Config(Path(tempdir))
        profile = load_ffmpeg_profile(loader, "simple")

        assert profile.input == ["i1", "i2"]
        assert profile.output == ["o1", "o2"]
