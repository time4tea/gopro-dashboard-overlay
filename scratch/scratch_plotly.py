import datetime

import plotly.graph_objs as go

from gopro_overlay import timeseries_process
from gopro_overlay.gpx import load_timeseries
from gopro_overlay.units import units

if __name__ == "__main__":
    ts = load_timeseries("/home/richja/Downloads/Morning_Ride-20210918.gpx", units)

    dt_min = datetime.datetime(2021, 9, 18, 9, 12, 0, tzinfo=datetime.timezone.utc)
    dt_max = datetime.datetime(2021, 9, 18, 9, 15, 0, tzinfo=datetime.timezone.utc)

    # timeseries = gpx_timeseries.clip_to_datetimes(dt_min, dt_max)

    ts.backfill(datetime.timedelta(seconds=1))


    def missing(a, b):
        delta = b.dt - a.dt
        if delta > datetime.timedelta(seconds=1):
            print(f"{a.dt} {delta}")


    ts.process_deltas(missing)
    ts.process(timeseries_process.process_ses("point", lambda i: i.point, alpha=0.45))
    ts.process_deltas(timeseries_process.calculate_speeds())
    # ts.process(timeseries.process_ses("speed", lambda i: i.speed, alpha=0.45))
    ts.process(timeseries_process.calculate_odo())

    # for e in ts.items():
    #       if 7.5 <= e.odo.to("mile").magnitude <= 8.5:
    #             print(e)

    x, y = zip(*[(e.odo.to("mile"), e.speed.to("MPH")) for e in ts.items() if e.speed is not None])
    fig = go.Figure(data=go.Scatter(x=x, y=y))
    fig.update_layout(height=1000, width=1200)
    fig.show()


