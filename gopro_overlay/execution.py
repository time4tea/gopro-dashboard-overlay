from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from asyncio import Protocol, StreamWriter
from multiprocessing import Process


class InProcessExecution:

    def __init__(self, redirect: bool = False, popen=subprocess.Popen):
        self.redirect = redirect
        self.popen = popen

    def execute(self, cmd):
        try:
            print(f"Running FFMPEG as '{' '.join(cmd)}'")
            if self.redirect:
                with open(self.redirect, "w") as std:
                    process = self.popen(cmd, stdin=subprocess.PIPE, stdout=std, stderr=std)
            else:
                process = self.popen(cmd, stdin=subprocess.PIPE, stdout=None, stderr=None)

            try:
                yield process.stdin
            finally:
                process.stdin.flush()
            process.stdin.close()
            # really long wait as FFMPEG processes all the mpeg input file - not sure how to prevent this atm
            process.wait(5 * 60)
        except FileNotFoundError:
            raise IOError("Unable to start the 'ffmpeg' process - is FFMPEG installed?") from None
        except BrokenPipeError:
            if self.redirect:
                print("FFMPEG Output:")
                with open(self.redirect) as f:
                    print("".join(f.readlines()), file=sys.stderr)
            raise IOError("FFMPEG reported an error - can't continue") from None


class CopyingProtocol(Protocol):

    def __init__(self, writer: StreamWriter) -> None:
        super().__init__()
        self.writer = writer

    def data_received(self, data: bytes) -> None:
        self.writer.write(data)

    def connection_lost(self, exc: Exception | None) -> None:
        print("Lost")
        self.writer.close()


async def connect_input(input, writer):
    loop = asyncio.get_event_loop()

    proto = CopyingProtocol(writer)
    await loop.connect_read_pipe(lambda: proto, input)


async def exec_copy_streams(input, cmd):
    process = await asyncio.create_subprocess_exec(cmd, stdin=subprocess.PIPE)

    await connect_input(input=input, writer=process.stdin)

    await process.wait()


class ForkingExecution:
    def __init__(self, cmd, redirect, popen=subprocess.Popen):
        self.cmd = cmd
        self.redirect = redirect
        self.popen = popen

    @staticmethod
    def child(input, cmd):
        asyncio.run(exec_copy_streams(input, cmd))

    def execute(self):

        child_in, parent_out = os.pipe()

        process = Process(target=ForkingExecution.child, args=(child_in, self.cmd))

        process.start()
        try:
            yield parent_out
        except Exception:
            process.terminate()
