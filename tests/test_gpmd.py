import inspect
import os
from array import array
from pathlib import Path

from gopro_overlay import gpmd
from gopro_overlay.gpmd import GPSVisitor, GPSFix, GPS5


def load_meta(name):
    sourcefile = Path(inspect.getfile(load_meta))

    meta_dir = sourcefile.parents[0].joinpath("meta")

    with open(os.path.join(meta_dir, name), "rb") as f:
        arr = array("b")
        arr.frombytes(f.read())
        return arr


def test_load_hero6_raw():
    items = list(gpmd.GPMDParser(load_meta("hero6.raw")).items())
    assert len(items) == 1

    devc = items[0]
    assert devc.with_type("DVNM")[0].interpret() == "Hero6 Black"
    assert devc.with_type("TICK")[0].interpret() == 342433
    assert devc.fourcc == "DEVC"
    assert devc.itemset == {"DVNM", "DVID", "TICK", "STRM"}
    assert len(devc) == 14


def test_debugging_visitor_at_least_doesnt_blow_up():
    items = list(gpmd.GPMDParser(load_meta("hero6.raw")).items())
    for i in items:
        i.accept(DebuggingVisitor())


def test_load_hero5_raw():
    items = list(gpmd.GPMDParser(load_meta("hero5.raw")).items())
    assert len(items) == 1

    assert items[0].with_type("DVNM")[0].interpret() == "Camera"

    def assert_components(count, components):
        print(components)
        assert count == 1
        assert components.samples == 18
        assert components.dop == 6.06
        assert components.fix == GPSFix.LOCK_3D
        assert len(components.points) == 18
        assert len(components.points) == components.samples
        assert components.scale == (10000000, 10000000, 1000, 1000, 100)
        assert components.points[0] == GPS5(lat=331264969, lon=-1173273542, alt=-20184, speed=167, speed3d=19)

    items[0].accept(GPSVisitor(converter=assert_components))


def test_load_hero6_ble_raw():
    items = list(gpmd.GPMDParser(load_meta("hero6+ble.raw")).items())
    assert len(items) == 2

    assert items[0].with_type("DVNM")[0].interpret() == "Hero6 Black"
    assert items[1].with_type("DVNM")[0].interpret() == "SENSORB6"


def test_load_extracted_meta():
    items = list(gpmd.GPMDParser(load_meta("gopro-meta.gpmd")).items())

    for i in items:
        i.accept(GPSVisitor(converter=lambda count, components: print(components)))

    assert len(items) == 707


class DebuggingVisitor:

    def __init__(self):
        self._indent = 0

    def __getattr__(self, item):
        if item.startswith("vi_"):
            return lambda a: print(f"{' ' * self._indent}{a}")
        if item.startswith("vic_"):
            def thing(a, b):
                print(f"{' ' * self._indent}{a}")
                self._indent += 1

                return self

            return thing
        raise AttributeError(item)

    def v_end(self):
        self._indent -= 1
