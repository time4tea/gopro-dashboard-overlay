from pathlib import Path

from gopro_overlay.log import fatal


def assert_file_exists(path: Path) -> Path:
    if not path.exists():
        fatal(f"{path}: File not found")
    return path
