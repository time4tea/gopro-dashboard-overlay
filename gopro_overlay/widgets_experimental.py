import bisect

import matplotlib

matplotlib.use("Agg")

from PIL import Image


class SparkLine:

    def __init__(self, at, timeseries, dt):
        self.at = at
        self.timeseries = timeseries
        self.dt = dt
        self.cadences = None
        self.dts = None

    def _maybe_init(self):

        self.cadences = []
        self.dts = []

        def process(entry):
            self.cadences.append(entry.cad.magnitude if entry.cad else 0)
            self.dts.append(entry.dt)

        if not self.cadences:
            self.timeseries.process(process)

    def draw(self, image, draw):
        import matplotlib.pyplot as plt

        self._maybe_init()

        data = self.cadences

        fig, ax = plt.subplots(1, 1, figsize=(4, 0.25))
        ax.plot(data, "r")
        for k, v in ax.spines.items():
            v.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])

        current_dt = self.dt()
        dt_index = bisect.bisect_right(self.dts, current_dt)

        plt.plot(dt_index, data[dt_index], 'wo')

        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        ax.fill_between(range(len(data)), data, len(data) * [min(data)], color="red", alpha=0.2)

        fig.canvas.draw()

        # PIL Conversion...
        sparkline = Image.frombytes("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba().tobytes())

        image.paste(sparkline, self.at.tuple())
