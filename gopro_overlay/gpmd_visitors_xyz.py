import collections

from gopro_overlay.point import Point3

XYZComponents = collections.namedtuple("XYZComponents", ["timestamp", "samples_total", "scale", "temp", "points"])


# noinspection PyPep8Naming
class XYZStreamVisitor:

    def __init__(self, on_end):
        self._on_end = on_end
        self._samples_total = None
        self._timestamp = None
        self._scale = None
        self._temperature = None
        self._type = None
        self._points = None

    def vi_STMP(self, item):
        self._timestamp = item.interpret()

    def vi_TSMP(self, item):
        self._samples_total = item.interpret()

    def vi_ORIN(self, item):
        pass

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_TMPC(self, item):
        self._temperature = item.interpret()

    def vi_ACCL(self, item):
        self._type = item.fourcc
        self._points = item.interpret(self._scale)

    def vi_GYRO(self, item):
        self._type = item.fourcc
        self._points = item.interpret(self._scale)

    def v_end(self):
        self._on_end(
            XYZComponents(
                timestamp=self._timestamp,
                samples_total=self._samples_total,
                scale=self._scale,
                temp=self._temperature,
                points=self._points,
            )
        )


class XYZComponentConverter:

    def __init__(self, on_item):
        self._on_item = on_item

    def convert(self, counter, components):
        for index, point in enumerate(components.points):
            self._on_item((counter, index, Point3(point.x, point.y, point.z)))


# noinspection PyPep8Naming
class XYZVisitor:

    def __init__(self, name, on_item):
        self._counter = 0
        self._name = name
        self._on_item = on_item

    def vic_DEVC(self, item, contents):
        self._counter += 1
        return self

    def vic_STRM(self, item, contents):
        if self._name in contents:
            return XYZStreamVisitor(on_end=lambda i: self._on_item(self._counter, i))

    def v_end(self):
        pass
