from typing import Any

from gopro_overlay.log import log
from gopro_overlay.timing import PoorTimer
from gopro_overlay.widgets.widgets import Widget


class ProfiledWidget(Widget):

    def __init__(self, name: str, level: int, widget: Widget):
        self.widget = widget
        self.timer = PoorTimer(name, level)

    def draw(self, image, draw):
        with self.timer.timing(doprint=False):
            self.widget.draw(image, draw)


class WidgetProfiler:

    def __init__(self):
        self.widgets = []

    def decorate(self, name: str, level: int, widget: Any):
        widget = ProfiledWidget(name, level, widget)

        self.widgets.append(widget)

        return widget

    def print(self):
        for widget in reversed(self.widgets):
            log(widget.timer)
