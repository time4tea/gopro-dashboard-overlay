from progressbar import utils
from progressbar.widgets import FormatWidgetMixin, TimeSensitiveWidgetBase


class Rate(FormatWidgetMixin, TimeSensitiveWidgetBase):
    '''
    WidgetBase for showing the change per second == rate
    '''

    def __init__(
            self, format='%(scaled)5.1f/s', **kwargs):
        FormatWidgetMixin.__init__(self, format=format, **kwargs)
        TimeSensitiveWidgetBase.__init__(self, **kwargs)

    def _speed(self, value, elapsed):
        return float(value) / elapsed

    def __call__(self, progress, data, value=None, total_seconds_elapsed=None):
        if value is None:
            value = data['value']

        elapsed = utils.deltas_to_seconds(
            total_seconds_elapsed,
            data['total_seconds_elapsed'])

        data['scaled'] = self._speed(value, elapsed)
        return FormatWidgetMixin.__call__(self, progress, data)
