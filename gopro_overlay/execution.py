from __future__ import annotations

import subprocess

from gopro_overlay.log import log


class InProcessExecution:

    def __init__(self, redirect=None, popen=subprocess.Popen):
        self.redirect = redirect
        self.popen = popen

    def execute(self, cmd):
        try:
            log(f"Executing {cmd}")
            if self.redirect:
                with open(self.redirect, "w") as std:
                    process = self.popen(cmd, stdin=subprocess.PIPE, stdout=std, stderr=std)
            else:
                process = self.popen(cmd, stdin=subprocess.PIPE, stdout=None, stderr=None)

            try:
                yield process.stdin
            finally:
                if not process.stdin.closed:
                    process.stdin.flush()
                    process.stdin.close()
                # really long wait as FFMPEG processes all the mpeg input file - not sure how to prevent this atm
                log("Waiting for ffmpeg to complete...")
                returncode = process.wait(5 * 60)
                log(f"FFMPEG Exited with status code: {returncode}")
        except FileNotFoundError:
            raise IOError(f"Unable to execute the process - is '{cmd[0]}' installed") from None
        except BrokenPipeError:
            if self.redirect:
                log("FFMPEG Output:")
                with open(self.redirect) as f:
                    log("".join(f.readlines()))
            raise IOError(f"Process {cmd[0]} failed") from None
