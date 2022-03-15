import json
import pathlib

from gopro_overlay.ffmpeg import FFMPEGOptions


def load_ffmpeg_profile(dir: pathlib.Path, profile: str):
    profile_file = dir / "ffmpeg-profiles.json"
    if not profile_file.exists():
        raise ValueError(f"Expecting to find an FFMPEG Profile configuration at: {profile_file}")
    with open(profile_file) as pf:
        profile_json = json.load(pf)

    if profile not in profile_json:
        raise ValueError(f"Can't find key {profile} in {profile_file}")

    selected = profile_json[profile]

    if "input" in selected and type(selected["input"]) == list:
        input_options = selected["input"]
    else:
        raise ValueError(f"Can't find input option list for key {profile} in {profile_file}")

    if "output" in selected and type(selected["output"]) == list:
        output_options = selected["output"]
    else:
        raise ValueError(f"Can't find output option list for key {profile} in {profile_file}")

    return FFMPEGOptions(input=input_options, output=output_options)
