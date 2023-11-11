from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Optional

from gopro_overlay.execution import InProcessExecution
from gopro_overlay.log import log
from gopro_overlay.process import run, invoke


class FFMPEG:
    def __init__(self, location: Optional[Path] = None, binary="ffmpeg", print_cmds=False, invoke_fn=invoke):
        self.invoke_fn = invoke_fn
        self.print_cmds = print_cmds
        self.location = location
        self.binary = binary

    def ffmpeg(self):
        return FFMPEG(self.location, "ffmpeg", invoke_fn=self.invoke_fn)

    def ffprobe(self):
        return FFMPEG(self.location, "ffprobe", invoke_fn=self.invoke_fn)

    def is_installed(self):
        try:
            self.invoke(["-version"])
            return True
        except FileNotFoundError:
            return False

    def version(self):
        ffmpeg_output = str(self.invoke(["-version"]).stdout)
        version_line = ffmpeg_output.split("\n")[0]
        match = re.search(r"ffmpeg version ([\w.+-]+)", version_line)
        if match is None:
            raise ValueError(f"Unable to determine ffmpeg version from: {version_line}")
        return match.group(1)

    def libx264_is_installed(self):
        output = self.invoke(["-v", "quiet", "-codecs"]).stdout
        libx264s = [x for x in output.split('\n') if "libx264" in x]
        return len(libx264s) > 0

    def _path(self):
        if self.location is not None:
            return self.location / self.binary
        else:
            return self.binary

    def run(self, args, **kwargs):
        args_ = [self._path(), *args]
        if self.print_cmds:
            log(f"Running {args_}")
        return run(args_, **kwargs)

    def invoke(self, args, **kwargs):
        args_ = [self._path(), *args]
        if self.print_cmds:
            log(f"Running {args_}")
        return self.invoke_fn(args_, **kwargs)

    def execute(self, execution: InProcessExecution, args):
        yield from execution.execute([self._path(), *args])

    async def _stream(self, args, cb):
        process = await asyncio.create_subprocess_exec(
            self._path(), *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        while True:
            read = await process.stdout.read(1024 * 1024)
            if len(read) != 0:
                cb(read)
            else:
                return await process.wait()

    def stream(self, args, cb):
        if self.print_cmds:
            log(f"Running {args}")

        loop = asyncio.get_event_loop()
        task = self._stream(args, cb)
        return loop.run_until_complete(task)



if __name__ == "__main__":
    print(FFMPEG().libx264_is_installed())
