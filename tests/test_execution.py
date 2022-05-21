import contextlib

from gopro_overlay.execution import InProcessExecution, ForkingExecution


@contextlib.contextmanager
def do_execute(execution, cmd):
    yield from execution.execute(cmd)


def test_in_process_execution():
    execution = InProcessExecution(redirect="/tmp/foo")
    with do_execute(execution, ["cat"]) as out:
        out.write("Hello".encode())


def test_forking_execution():
    execution = ForkingExecution(redirect="/tmp/foo")
    with do_execute(execution, ["cat"]) as out:
        out.write("Hello".encode())
        out.write("Hello".encode())
        out.write("Hello".encode())
        out.write("Hello".encode())
        out.write("Hello".encode())
        out.write("Hello".encode())
