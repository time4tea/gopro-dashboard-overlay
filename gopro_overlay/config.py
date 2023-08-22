import dataclasses
import json
import pathlib
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True)
class ConfigFile:
    content: Any
    location: pathlib.Path

    def exists(self):
        return self.content is not None

class Config:

    def __init__(self, location: Path):
        self.location = location

    def load(self, explanation:str, name:str) -> ConfigFile:
        r = self.maybe(name)
        if not r.exists():
            raise ValueError(f"Expecting to find an {explanation} configuration at: {r.location}")
        return r

    def maybe(self, name: str) -> ConfigFile:
        p = self.location / name
        if p.exists():
            with open(p) as pf:
                return ConfigFile(content=json.load(pf), location=p)
        return ConfigFile(content=None, location=p)
