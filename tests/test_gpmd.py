import datetime
import inspect
import os
from array import array
from pathlib import Path

from gopro_overlay import gpmd
from gopro_overlay.gpmd import GPSVisitor, GPSFix, GPS5, XYZVisitor, XYZComponentConverter, GPS5EntryConverter, XYZ
from gopro_overlay.point import Point
from gopro_overlay.units import units


def load_meta(name):
    sourcefile = Path(inspect.getfile(load_meta))

    meta_dir = sourcefile.parents[0].joinpath("meta")

    with open(os.path.join(meta_dir, name), "rb") as f:
        arr = array("b")
        arr.frombytes(f.read())
        return arr


def load(name):
    return list(gpmd.GPMDParser(load_meta(name)).items())


def test_load_hero6_raw():
    items = load("hero6.raw")
    assert len(items) == 1

    devc = items[0]
    assert devc.with_type("DVNM")[0].interpret() == "Hero6 Black"
    assert devc.with_type("TICK")[0].interpret() == 342433
    assert devc.fourcc == "DEVC"
    assert devc.itemset == {"DVNM", "DVID", "TICK", "STRM"}
    assert len(devc) == 14


def test_debugging_visitor_at_least_doesnt_blow_up():
    items = load("hero5.raw")
    for i in items:
        i.accept(DebuggingVisitor())


def test_load_hero5_raw_gps5():
    items = load("hero5.raw")
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
        assert components.points[0] == GPS5(lat=33.1264969, lon=-117.3273542, alt=-20.184, speed=0.167, speed3d=0.19)

    items[0].accept(GPSVisitor(converter=assert_components))


def test_load_hero5_raw_entry():
    items = load("hero5.raw")
    assert len(items) == 1

    assert items[0].with_type("DVNM")[0].interpret() == "Camera"

    counter = [0]

    def assert_item(entry):
        counter[0] += 1
        if entry.packet_index.magnitude == 0:
            assert entry.dt == datetime.datetime(2017, 4, 17, 17, 31, 3, tzinfo=datetime.timezone.utc)
            assert entry.dop.magnitude == 6.06
            assert entry.packet.magnitude == 1
            assert entry.packet_index.magnitude == 0
            assert str(entry.point) == str(Point(lat=33.1264969, lon=-117.3273542))  # float comparison
            assert entry.speed == units.Quantity(0.167, units.mps)
            assert entry.alt == units.Quantity(-20.184, units.m)

    converter = GPS5EntryConverter(units=units, on_item=assert_item)

    items[0].accept(GPSVisitor(converter=converter.convert))

    assert counter[0] == 18


def test_load_hero5_raw_accl():
    items = load("hero6.raw")
    assert len(items) == 1

    def assert_components(count, components):
        print(components)
        assert count == 1
        assert components.samples_total == 806
        assert len(components.points) == 204
        assert components.scale == (418,)
        assert components.points[0] == XYZ(y=9.97846889952153, x=0.05502392344497608, z=3.145933014354067)

    items[0].accept(XYZVisitor("ACCL", on_item=assert_components))


def test_load_hero6_ble_raw():
    items = load("hero6+ble.raw")
    assert len(items) == 2

    assert items[0].with_type("DVNM")[0].interpret() == "Hero6 Black"
    assert items[1].with_type("DVNM")[0].interpret() == "SENSORB6"


def test_load_extracted_meta():
    assert len(load("gopro-meta.gpmd")) == 707


def test_load_and_visit_extracted_meta():
    items = load("gopro-meta.gpmd")
    assert len(items) == 707

    visitor = CountingVisitor()
    [i.accept(visitor) for i in items]

    assert visitor.count == 108171


def test_load_accel_meta():
    items = load("rotation-example.gpmd")

    converter = XYZComponentConverter(on_item=lambda i: print(i))
    visitor = XYZVisitor("ACCL", on_item=converter.convert)

    for i in items:
        i.accept(visitor)


def test_load_rotation_meta():
    items = load("rotation-example.gpmd")

    converter = XYZComponentConverter(on_item=lambda i: print(i))
    visitor = XYZVisitor("GYRO", on_item=converter.convert)

    for i in items:
        i.accept(visitor)


def test_debug_rotation_meta():
    items = load("rotation-example.gpmd")

    visitor = DebuggingVisitor()

    for i in items:
        i.accept(visitor)


class GRAVisitor:

    def __init__(self):
        self._scale = None

    def vic_DEVC(self, i, s):
        return self

    def vic_STRM(self, i, s):
        if "GRAV" in s:
            return self

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_GRAV(self, item):
        vectors = item.interpret(self._scale)
        print(vectors)

    def v_end(self):
        pass


def test_load_gravity_meta():
    items = load("rotation-example.gpmd")

    for i in items:
        i.accept(GRAVisitor())


class CountingVisitor:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def __getattr__(self, item):
        if item.startswith("vi_"):
            return lambda x: self.inc()
        if item.startswith("vic_"):
            return lambda i, s: self

    def v_end(self):
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
