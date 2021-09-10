import timeseries
from gpmd import timeseries_from
from overlayer import calculate_speeds
from units import units

if __name__ == "__main__":
    filename = "GH020064"

    gopro_timeseries = timeseries_from(f"/data/richja/gopro/{filename}.MP4")

    from gpx import load_timeseries

    gpx_timeseries = load_timeseries("/home/richja/Downloads/City_Loop.gpx", units)

    wanted_timeseries = gpx_timeseries.clip_to(gopro_timeseries)

    wanted_timeseries.process_deltas(calculate_speeds)
    wanted_timeseries.process(timeseries.process_ses("azi2", lambda i: i.azi, alpha=0.2))

    for item in wanted_timeseries.items():
        print(f"{item.azi}  {item.azi2}")

    pass
