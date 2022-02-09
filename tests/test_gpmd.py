import inspect
import itertools
import os
from array import array
from pathlib import Path

from gopro_overlay import gpmd
from gopro_overlay.gpmd import XYZ, GPSVisitor
from gopro_overlay.point import Point3
from gopro_overlay.units import units


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

    assert devc.fourcc == "DEVC"
    assert devc.is_container


def test_load_hero5_raw():
    items = list(gpmd.GPMDParser(load_meta("hero5.raw")).items())

    for i in items:
        i.accept(GPSVisitor(units=units, max_dop=100, on_item=lambda i: print(i), on_drop=lambda e: print(e)))

    assert len(items) == 1


def test_load_hero6_ble_raw():
    items = list(gpmd.GPMDParser(load_meta("hero6+ble.raw")).items())
    assert len(items) == 1


def test_load_extracted_meta():
    items = list(gpmd.GPMDParser(load_meta("gopro-meta.gpmd")).items())

    for i in items:
        i.accept(GPSVisitor(units=units, max_dop=100, on_item=lambda i: print(i), on_drop=lambda e: print(e)))

    assert len(items) == 707


class NopVisitor:

    def visitContainer(self):
        return self

    def visitItem(self):
        pass


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


