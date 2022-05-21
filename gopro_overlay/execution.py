from __future__ import annotations

import queue
import subprocess
import sys
import threading
from queue import Queue


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


class ThreadedTransport:

    def __init__(self, q, stream):
        self.q = q
        self.stream = stream
        self.should_stop = threading.Event()

    def run(self):
        try:
            while True:
                try:
                    to_send = self.q.get(timeout=0.1)
                except queue.Empty:
                    to_send = None
                if to_send:
                    self.stream.write(to_send)
                else:
                    if self.should_stop.is_set():
                        break
        finally:
            self.stream.close()

    def stop(self):
        self.should_stop.set()


class QueueWriter:
    def __init__(self, q):
        self.q = q

    def write(self, b):
        self.q.put(b)


class ThreadingExecution:
    def __init__(self, redirect=None):
        self.redirect = redirect
        self.popen = subprocess.Popen

    def execute(self, cmd):
        if self.redirect:
            with open(self.redirect, "w") as std:
                process = self.popen(cmd, stdin=subprocess.PIPE, stdout=std, stderr=std)
        else:
            process = self.popen(cmd, stdin=subprocess.PIPE, stdout=None, stderr=None)

        queue = Queue(maxsize=20)

        transport = ThreadedTransport(queue, process.stdin)

        thread = threading.Thread(target=transport.run)
        thread.start()

        yield QueueWriter(queue)

        transport.stop()

        thread.join(5 * 60)
        process.wait(5 * 60)
