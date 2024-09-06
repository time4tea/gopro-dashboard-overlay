from typing import Mapping

from .config import Config
from .ffmpeg_overlay import FFMPEGOptions
from .log import log

builtin_profiles = {
    "nvgpu": {
        "input": ["-hwaccel", "nvdec"],
        "output": ["-vcodec", "h264_nvenc", "-rc:v", "cbr", "-b:v", "25M", "-bf:v", "3", "-profile:v", "high", "-spatial-aq", "true", "-movflags", "faststart"]
    },
    "nnvgpu": {
        "input": ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"],
        "filter": "[0:v]scale_cuda=format=yuv420p[mp4_stream];[1:v]format=yuva420p,hwupload[overlay_stream];[mp4_stream][overlay_stream]overlay_cuda",
        "output": ["-vcodec", "h264_nvenc", "-rc:v", "cbr", "-b:v", "25M", "-bf:v", "3", "-profile:v", "main", "-spatial-aq", "true", "-movflags", "faststart"]
    },
    "mov": {
        "input": [],
        "output": ["-vcodec", "png"]
    },
    "vp9": {
        "input": [],
        "output": ["-vcodec", "vp9", "-pix_fmt", "yuva420p"]
    },
    "vp8": {
        "input": [],
        "output": ["-vcodec", "vp8", "-pix_fmt", "yuva420p", "-auto-alt-ref", "0"]
    },
    "mac_hevc": {
        "input": ["-hwaccel", "videotoolbox"],
        "output": ["-vcodec", "hevc_videotoolbox", "-q:v", "60"]
    },
    "mac": {
        "input": ["-hwaccel", "videotoolbox"],
        "output": ["-vcodec", "h264_videotoolbox", "-q:v", "60"]
    }
}


class FFMPEGProfiles:

    def __init__(self, config: Config):
        self.config = config

    def load_profile(self, name: str) -> FFMPEGOptions:
        config_file = self.config.maybe("ffmpeg-profiles.json")

        if config_file.exists():
            if name in config_file.content:
                log(f"Using *user-defined* profile: {name}")
                try:
                    return self.load_profile_content(config_file.content, name)
                except ValueError as e:
                    raise ValueError(f"{config_file.location}: {e}") from None

        if name in builtin_profiles:
            log(f"Using *built-in* profile: {name}")
            profile = builtin_profiles[name]
            return FFMPEGOptions(input=profile["input"], output=profile["output"], filter_spec=profile.get("filter", None))

        if config_file.exists():
            raise ValueError(f"Can't find key {name} in {config_file.location}, and it is also not a built-in profile")
        else:
            raise ValueError(f"{name} is not a built-in profile, and no config file found at {config_file.location}")

    def load_profile_content(self, content: Mapping, name: str) -> FFMPEGOptions:

        selected = content[name]

        if "input" in selected and isinstance(selected["input"], list):
            input_options = selected["input"]
        else:
            raise ValueError(f"Can't find input option list for key {name}")

        if "output" in selected and isinstance(selected["output"], list):
            output_options = selected["output"]
        else:
            raise ValueError(f"Can't find output option list for key {name}")

        filter_spec = None

        if "filter" in selected:
            if isinstance(selected["filter"], str):
                filter_spec = selected["filter"]
            else:
                raise ValueError("'filter' specified, but wasn't a string")

        return FFMPEGOptions(input=input_options, output=output_options, filter_spec=filter_spec)


def load_ffmpeg_profile(config: Config, name: str) -> FFMPEGOptions:
    return FFMPEGProfiles(config).load_profile(name)
