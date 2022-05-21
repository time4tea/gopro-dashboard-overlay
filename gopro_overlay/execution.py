from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from asyncio import Protocol, StreamWriter
from multiprocessing import Process

from gopro_overlay.timing import PoorTimer


class InProcessExecution:

    def __init__(self, redirect=None, popen=subprocess.Popen):
        self.redirect = redirect
        self.popen = popen

    def execute(self, cmd):
        try:
            print(f"Executing '{' '.join(cmd)}'")
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
            raise IOError(f"Unable to execute the process - is '{cmd[0]}' installed") from None
        except BrokenPipeError:
            if self.redirect:
                print("FFMPEG Output:")
                with open(self.redirect) as f:
                    print("".join(f.readlines()), file=sys.stderr)
            raise IOError(f"Process {cmd[0]} failed") from None


class CopyingProtocol(Protocol):

    def __init__(self, writer: StreamWriter) -> None:
        super().__init__()
        self.timer = PoorTimer(name="CopyProtocol")
        self.writer = writer

    def data_received(self, data: bytes) -> None:
        print(f"Got {len(data)} bytes")
        self.timer.time(lambda: self.writer.write(data))

    def connection_lost(self, exc: Exception | None) -> None:
        self.writer.close()
        print(self.timer)


async def connect_input(input, writer):
    loop = asyncio.get_event_loop()

    proto = CopyingProtocol(writer)
    await loop.connect_read_pipe(lambda: proto, input)


async def exec_copy_streams(input, redirect, cmd):

    limit = 1920 * 1080 * 4

    if redirect:
        with open(redirect, "w") as std:
            process = await asyncio.create_subprocess_exec(*cmd, stdin=subprocess.PIPE, stdout=std, stderr=std, limit=limit)
    else:
        process = await asyncio.create_subprocess_exec(*cmd, stdin=subprocess.PIPE, limit=limit)

    await connect_input(input=input, writer=process.stdin)

    await process.wait()


class ForkingExecution:
    def __init__(self, redirect=None):
        self.redirect = redirect

    @staticmethod
    def child(input, output, redirect, cmd):
        os.close(output)
        return asyncio.run(exec_copy_streams(os.fdopen(input, "rb"), redirect, cmd))

    def execute(self, cmd):

        child_in, parent_out = os.pipe()

        process = Process(
            target=ForkingExecution.child,
            args=(child_in, parent_out, self.redirect, cmd),
            name=f"iobuffer process for {cmd[0]}"
        )

        process.start()
        os.close(child_in)
        try:
            out = os.fdopen(parent_out, "wb")
            yield out
            out.close()

            print("Waiting for process to finish...")
            process.join()
        except Exception as e:
            print(f"Exception! {e}")
            process.terminate()
