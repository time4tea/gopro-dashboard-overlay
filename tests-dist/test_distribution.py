import contextlib
import os
import subprocess
from pathlib import Path

mydir = Path(os.path.dirname(__file__))
top = mydir.parent.absolute()

distribution = os.environ.get("DISTRIBUTION", os.path.join(top, "tmp/dist-test/venv"))

expected_binaries = list(map(lambda f: os.path.join(distribution, "bin", f), os.listdir(os.path.join(top, "bin"))))


@contextlib.contextmanager
def working_directory(d):
    current = os.getcwd()
    os.chdir(d)
    try:
        yield
    except Exception as e:
        raise e from None
    finally:
        os.chdir(current)


def test_expected_binaries_are_installed():
    for thing in expected_binaries:
        assert os.path.exists(thing)


def test_can_at_least_show_help_for_all_binaries():
    """need to set 'env' else PyCharm will set PYTHONPATH, and things will work that shouldn't"""
    with working_directory("/tmp"):
        for thing in expected_binaries:
            cmd = [thing, "--help"]
            process = subprocess.run(cmd, check=True, env={})
            assert process.returncode == 0


# this is kind of a hack. works on my machine
def test_init_pys_are_in_right_subfolders():
    path = os.path.join(top, "gopro_overlay")
    expected_subpackages = list(
        map(os.path.basename, filter(
            os.path.isdir,
            map(lambda f: os.path.join(path, f), filter(lambda f: not f.startswith("__"), os.listdir(path)))
        ))
    )
    assert len(expected_subpackages) > 0
    for p in expected_subpackages:
        assert os.path.exists(os.path.join(distribution, "lib", "python3.8", "site-packages", "gopro_overlay", p, "__init__.py"))
