from pathlib import Path
from zoneinfo import ZoneInfo

import gpxpy
import matplotlib.pyplot as plot

from gopro_overlay import gpx, timeseries_process, loading
from gopro_overlay.ffmpeg import find_recording
from gopro_overlay.loading import framemeta_from
from gopro_overlay.framemeta_gpx import timeseries_to_framemeta, merge_gpx_with_gopro
from gopro_overlay.gpmd import GPS_FIXED_VALUES
from gopro_overlay.units import units


def points_in(gpx):
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                yield point


class Cursor(object):
    def __init__(self, ax):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line

        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        plot.draw()


if __name__ == "__main__":
    folder = Path("render/contrib/bad-gps-speed-issue-92")
    base_name = "GH010268"

    gpx_file_path = folder / f"_{base_name}.gpx"
    gpx_with_calculated_speeds_path = folder / f"speed_{base_name}.gpx"
    gopro_movie_path = folder / f"{base_name}.MP4"

    # Load GPX1.0 file with speeds
    with gpx_with_calculated_speeds_path.open('r') as gpx_file:
        gpx_with_speeds = gpxpy.parse(gpx_file)

    # Calculate speeds in bare GPX File
    gpx_without_speed_ts = gpx.load_timeseries(gpx_file_path, units)
    gpx_without_speed_fm = timeseries_to_framemeta(gpx_without_speed_ts, units=units)
    locked_2d = lambda e: e.gpsfix in GPS_FIXED_VALUES
    gpx_without_speed_fm.process_deltas(timeseries_process.calculate_speeds(), skip=10 * 3, filter_fn=locked_2d)
    fm_dates, fm_speeds = zip(*[(e.dt, e.cspeed.to("kph").m if e.cspeed else None) for e in gpx_without_speed_fm.items()])

    gpx_times = [point.time.astimezone(ZoneInfo('UTC')) for point in points_in(gpx_with_speeds)]
    gpx_speeds = [p.speed for p in points_in(gpx_with_speeds)]

    # Calculate speeds from GoPro File
    gopro = loading.load_gopro(
        gopro_movie_path,
        units
    )

    gopro_file_fm = gopro.framemeta

    gopro_with_gpx_fm = gopro_file_fm.clone()

    gopro_file_fm.process_deltas(timeseries_process.calculate_speeds(), skip=18 * 3, filter_fn=locked_2d)

    gopro_act_dates, gopro_act_speeds = zip(*[(e.dt, e.speed.to("kph").m if e.speed else None) for e in gopro_file_fm.items() if locked_2d(e)])
    gopro_calc_dates, gopro_calc_speeds = zip(*[(e.dt, e.cspeed.to("kph").m if e.cspeed else None) for e in gopro_file_fm.items() if locked_2d(e)])

    # Overlay GPX File into GoPro File
    merge_gpx_with_gopro(gpx_without_speed_ts, gopro_with_gpx_fm)
    gopro_with_gpx_fm.process_deltas(timeseries_process.calculate_speeds(), skip=18 * 3, filter_fn=locked_2d)

    gopro_with_gpx_act_dates, gopro_with_gpx_act_speeds = zip(*[(e.dt, e.speed.to("kph").m if e.speed else None) for e in gopro_with_gpx_fm.items() if locked_2d(e)])
    gopro_with_gpx_calc_dates, gopro_with_gpx_calc_speeds = zip(*[(e.dt, e.cspeed.to("kph").m if e.cspeed else None) for e in gopro_with_gpx_fm.items() if locked_2d(e)])

    # Plot some stuff

    plot.plot_date(gpx_times, gpx_speeds, label="Speeds Supplied", ms=1)
    plot.plot_date(fm_dates, fm_speeds, label="Speeds Calculated from GPX", ms=1)
    # plot.plot_date(gopro_act_dates, gopro_act_speeds, label="Speeds from MP4", ms=1)
    # plot.plot_date(gopro_calc_dates, gopro_calc_speeds, label="Speeds Calculated from MP4", ms=1)

    plot.plot_date(gopro_with_gpx_act_dates, gopro_with_gpx_act_speeds, label="Speeds actual from merged", ms=2)
    plot.plot_date(gopro_with_gpx_calc_dates, gopro_with_gpx_calc_speeds, label="Speeds calc from merged", ms=2)

    plot.legend()
    plot.xlabel('GPS Time')
    plot.ylabel('Speed (kph)')

    fix, ax = plot.subplots()
    cursor = Cursor(ax)

    plot.connect("motion_notify_event", cursor.mouse_move)

    plot.show()
