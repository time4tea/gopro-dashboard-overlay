import progressbar

from gopro_overlay import progress_frames


class ProgressTracker:

    def start(self, count):
        pass

    def update(self, processed):
        pass

    def complete(self):
        pass


class ProgressBarProgress(ProgressTracker):

    def __init__(self, title, delta:bool=False, transfer:bool=False):
        self.progress = None
        self.title = title
        self.rate = not transfer
        self.delta = delta
        self.total = 0

    def _rate_widgets(self):
        return ' [', progress_frames.Rate() , '] '

    def _transfer_widgets(self):
        return ' [', progressbar.DataSize() , '] ', ' [', progressbar.FileTransferSpeed() , '] '

    def start(self, count=None):
        if count:
            widgets = [
                f'{self.title}: ',
                progressbar.Counter(format="{value:,}", new_style=True),
                ' [', progressbar.Percentage(), '] ',
                *(self._rate_widgets() if self.rate else self._transfer_widgets()),
                progressbar.Bar(), ' ', progressbar.ETA()
            ]
        else:
            widgets = [
                f'{self.title}: ',
                progressbar.Counter(format="{value:,}", new_style=True),
                *(self._rate_widgets() if self.rate else self._transfer_widgets()),
            ]

        self.progress = progressbar.ProgressBar(widgets=widgets, min_poll_interval=0.25, max_value=count)

    def update(self, processed):
        if self.delta:
            self.total += processed
        else:
            self.total = processed

        self.progress.update(self.total)

    def complete(self):
        self.progress.finish()