class StreamFindingVisitor:

    def __init__(self, wanted):
        self.wanted = wanted
        self._found = False

    def vic_DEVC(self, item, contents):
        return self

    def vic_STRM(self, item, contents):
        if self.wanted in contents:
            self._found = True

    def found(self):
        return self._found

    def v_end(self):
        pass


class DetermineTimestampOfFirstSHUTVisitor:
    """
        Seems like first SHUT frame is correlated with video frame?
        https://github.com/gopro/gpmf-parser/blob/151bb352ab3d1af8feb31e0cf8277ff86c70095d/demo/GPMF_demo.c#L414
    """

    def __init__(self):
        self._initial_timestamp = None

    @property
    def timestamp(self):
        return self._initial_timestamp

    def vic_DEVC(self, item, contents):
        if not self._initial_timestamp:
            return self

    def vi_STMP(self, item):
        self._initial_timestamp = item.interpret()

    def vic_STRM(self, item, contents):
        if "SHUT" in contents and not self._initial_timestamp:
            return self

    def v_end(self):
        pass
