import dbm
import math
from pathlib import Path

import geotiler
from PIL import ImageDraw

import timeseries
from geo import dbm_caching_renderer
from gpmd import timeseries_from
from overlayer import calculate_speeds, Extents
from units import units



if __name__ == "__main__":
    filename = "GH020064"

    gopro_timeseries = timeseries_from(f"/data/richja/gopro/{filename}.MP4", units)

    from gpx import load_timeseries

    gpx_timeseries = load_timeseries("/home/richja/Downloads/City_Loop.gpx", units)

    wanted_timeseries = gpx_timeseries.clip_to(gopro_timeseries)

    wanted_timeseries.process_deltas(calculate_speeds)
    wanted_timeseries.process(timeseries.process_ses("azi2", lambda i: i.azi, alpha=0.2))

    extents = Extents()
    wanted_timeseries.process(extents.accept)

    journey = Journey()
    wanted_timeseries.process(journey.accept)

    ourdir = Path.home().joinpath(".gopro-graphics")
    ourdir.mkdir(exist_ok=True)

    with dbm.ndbm.open(str(ourdir.joinpath("tilecache.ndbm")), "c") as db:
        render = dbm_caching_renderer(db)

        desired = 256
        hyp = int(math.sqrt((desired ** 2) * 2))

        print(f"desired = {desired}, hyp={hyp}")

        bounds = (
            (hyp / 2) - (desired / 2),
            (hyp / 2) - (desired / 2),
            (hyp / 2) + (desired / 2),
            (hyp / 2) + (desired / 2)
        )

        bbox = extents.bounding_box
        map = geotiler.Map(extent=(bbox[0].lon, bbox[0].lat, bbox[1].lon, bbox[1].lat), size=(hyp, hyp))

        plots = list((map.rev_geocode((location.lon, location.lat)) for location in journey.locations))

        orig = render(map)

        draw = ImageDraw.Draw(orig)
        for p in plots:
            draw.line(plots, fill=(255, 0, 0), width=4)

        crop = orig.crop(bounds)

        crop.show()

    print(extents.bounding_box)

    pass
