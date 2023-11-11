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

    def __init__(self, title):
        self.progress = None
        self.title = title

    def start(self, count):
        if count:
            widgets = [
                f'{self.title}: ',
                progressbar.Counter(format="{value:,}", new_style=True),
                ' [', progressbar.Percentage(), '] ',
                ' [', progress_frames.Rate(), '] ',
                progressbar.Bar(), ' ', progressbar.ETA()
            ]
        else:
            widgets = [
                f'{self.title} (#Items Unknown): ',
                progressbar.Counter(format="{value:,}", new_style=True),
                ' [', progress_frames.Rate(), '] ',
            ]

        self.progress = progressbar.ProgressBar(widgets=widgets, min_poll_interval=0.25, max_value=count)

    def update(self, processed):
        self.progress.update(processed)

    def complete(self):
        self.progress.finish()