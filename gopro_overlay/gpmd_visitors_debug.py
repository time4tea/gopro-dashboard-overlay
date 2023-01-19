from gopro_overlay.log import log


class DebuggingVisitor:

    def __init__(self):
        self._indent = 0

    def __getattr__(self, item):
        if item.startswith("vi_"):
            return lambda a: log(f"{' ' * self._indent}{a}")
        if item.startswith("vic_"):
            def thing(a, b):
                log(f"{' ' * self._indent}{a}")
                self._indent += 1

                return self

            return thing
        raise AttributeError(item)

    def v_end(self):
        self._indent -= 1
