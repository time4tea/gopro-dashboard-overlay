import contextlib
from pathlib import Path

from gopro_overlay.common import temp_file_name
from gopro_overlay.execution import InProcessExecution, ThreadingExecution


@contextlib.contextmanager
def do_execute(execution, cmd):
    yield from execution.execute(cmd)


def test_in_process_execution():
    filename = temp_file_name()
    execution = InProcessExecution(redirect=filename)
    with do_execute(execution, ["cat"]) as out:
        out.write("Hello".encode())

    assert Path(filename).read_text() == "Hello"


def test_threading_execution():
    filename = temp_file_name()
    execution = ThreadingExecution(redirect=filename)
    with do_execute(execution, ["cat"]) as out:
        out.write("Hello".encode())

    assert Path(filename).read_text() == "Hello"
