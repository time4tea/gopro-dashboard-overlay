import contextlib
import os
import subprocess
from pathlib import Path

from gopro_overlay.process import invoke, run
from tests.approval import approve_text

mydir = Path(os.path.dirname(__file__))
top = mydir.parent

if "DISTRIBUTION" in os.environ:
    distribution = Path(os.environ["DISTRIBUTION"])
else:
    distribution = top / "tmp/dist-test/venv"


def python_files_below(d):
    for root, dirs, files in os.walk(d):
        for name in [f for f in files if f.endswith(".py")]:
            rel = os.path.relpath(root, d)
            yield Path(rel, name)


expected_binaries = list(map(lambda f: distribution / "bin" / f, python_files_below(top / "bin")))

clip = top / "render" / "clip.MP4"
join_dir = top / "render" / "contrib" / "strange-gps-times"
to_join = join_dir / "GH010051.MP4"
joined = join_dir / "joined.MP4"


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
        assert thing.exists()


def test_can_at_least_show_help_for_all_binaries():
    """need to set 'env' else PyCharm will set PYTHONPATH, and things will work that shouldn't"""
    with working_directory("/tmp"):
        for thing in expected_binaries:
            cmd = [thing, "--help"]
            process = subprocess.run(cmd, check=True, env={})
            assert process.returncode == 0


# this is kind of a hack. works on my machine
def test_init_pys_are_in_right_subfolders():
    path = top / "gopro_overlay"
    expected_subpackages = list(
        map(os.path.basename, filter(
            os.path.isdir,
            map(lambda f: os.path.join(path, f), filter(lambda f: not f.startswith("__"), os.listdir(path)))
        ))
    )
    assert len(expected_subpackages) > 0
    for p in expected_subpackages:
        assert os.path.exists(
            os.path.join(distribution, "lib", "python3.11", "site-packages", "gopro_overlay", p, "__init__.py"))


def run_from_venv(cmd):
    run(cmd, env={})

def invoke_from_venv(cmd):
    return invoke(cmd, env={})

def test_maybe_renders_something():
    prog = distribution / "bin" / "gopro-dashboard.py"
    run_from_venv([prog, "--overlay-size", "1920x1080", clip, "/tmp/render-clip.MP4"])


def test_maybe_renders_something_kph():
    prog = distribution / "bin" / "gopro-dashboard.py"
    run_from_venv([prog, "--overlay-size", "1920x1080", "--units-speed", "kph", "--units-altitude", "inch", clip, "/tmp/render-clip-kph.MP4"])


def test_maybe_renders_something_example_layout():
    prog = distribution / "bin" / "gopro-dashboard.py"
    run_from_venv([prog, "--layout-xml", top / "examples/layout/layout-cairo-2704x1520.xml", clip, "/tmp/render-clip-example.MP4"])


@approve_text
def test_maybe_makes_a_csv():
    r = invoke_from_venv([(distribution / "bin" / "gopro-to-csv.py"), clip, "-"])
    print(r.stderr)
    return r.stdout


@approve_text
def test_maybe_makes_a_csv_every_second():
    r = invoke_from_venv([(distribution / "bin" / "gopro-to-csv.py"), "--every", "1", clip, "-"])
    print(r.stderr)
    return r.stdout


@approve_text
def test_maybe_makes_a_gpx():
    r = invoke_from_venv([(distribution / "bin" / "gopro-to-gpx.py"), clip, "-"])
    print(r.stderr)
    return r.stdout


@approve_text
def test_maybe_makes_a_gpx_every_second():
    r = invoke_from_venv([(distribution / "bin" / "gopro-to-gpx.py"), "--every", "1", clip, "-"])
    print(r.stderr)
    return r.stdout


def test_maybe_clips_something():
    prog = distribution / "bin" / "gopro-cut.py"
    run_from_venv([prog, "--start", "1", "--end", "2", clip, "/tmp/clip-clip.MP4"])


def test_maybe_clips_something_with_duration():
    prog = distribution / "bin" / "gopro-cut.py"
    run_from_venv([prog, "--start", "1", "--duration", "1", clip, "/tmp/clip-clip.MP4"])


def test_maybe_joins_some_files():
    prog = distribution / "bin" / "gopro-join.py"
    run_from_venv([prog, to_join, joined])


def test_maybe_rename_some_files_in_a_folder():
    prog = distribution / "bin" / "gopro-rename.py"
    output = invoke_from_venv([prog, "--dirs", join_dir]).stderr
    assert "GH010051.MP4" in output
    assert "20210905-062805.MP4" in output

    assert "GH020051.MP4" in output
    assert "20210905-074046.MP4" in output

    assert "GH030051.MP4" in output
    assert "20210905-083538.MP4" in output


def test_maybe_rename_some_files():
    prog = distribution / "bin" / "gopro-rename.py"
    print(prog)
    output = invoke_from_venv([prog, to_join]).stderr
    assert "GH010051.MP4" in output
    assert "20210905-062805.MP4" in output
