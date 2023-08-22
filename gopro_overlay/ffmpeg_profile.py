from gopro_overlay.config import Config
from gopro_overlay.ffmpeg_overlay import FFMPEGOptions


def load_ffmpeg_profile(config: Config, profile: str):
    config_file = config.load("FFMPEG Profile", "ffmpeg-profiles.json")

    profile_json = config_file.content

    if profile not in profile_json:
        raise ValueError(f"Can't find key {profile} in {config_file.location}")

    selected = profile_json[profile]

    if "input" in selected and type(selected["input"]) == list:
        input_options = selected["input"]
    else:
        raise ValueError(f"Can't find input option list for key {profile} in {config_file.location}")

    if "output" in selected and type(selected["output"]) == list:
        output_options = selected["output"]
    else:
        raise ValueError(f"Can't find output option list for key {profile} in {config_file.location}")

    filter_spec = None

    if "filter" in selected:
        if type(selected["filter"]) == str:
            filter_spec = selected["filter"]
        else:
            raise ValueError("'filter' specified, but wasn't a string")

    return FFMPEGOptions(input=input_options, output=output_options, filter_spec=filter_spec)
