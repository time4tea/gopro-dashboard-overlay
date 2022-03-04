import os
import random
import re
from datetime import timedelta
from pathlib import Path

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from gopro_overlay.font import load_font
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.gpmd import timeseries_from_data
from gopro_overlay.layout import Overlay
from gopro_overlay.layout_xml import layout_from_xml
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.units import units

mydir = os.path.dirname(__file__)


def tryint(s):
    try:
        return int(s)
    except:
        return s


def alphanum_key(s):
    return [tryint(c) for c in re.split(r'([0-9]+)', s)]


dimensions_by_file = {
    "05-moving-map.md": Dimension(256,256),
    "06-journey-map.md": Dimension(256,256),
}


def dimensions_for(filepath: str) -> Dimension:
    return dimensions_by_file.get(os.path.basename(filepath), Dimension(200, 100))


AUTO_HEADER = "<!-- \n\nAuto Generated File DO NOT EDIT \n\n-->"

if __name__ == "__main__":
    dest = os.path.join(os.path.dirname(mydir), "docs/xml/examples")
    example_dir = os.path.join(mydir, "examples")
    examples = sorted(
        list(filter(lambda it: it.endswith(".md"), os.listdir(example_dir))),
        key=alphanum_key
    )

    examples = [os.path.join(example_dir, it) for it in examples]

    renderer = CachingRenderer()

    with open(os.path.join(mydir, "..", "tests/meta/gopro-meta.gpmd"), "rb") as f:
        data = f.read()

    timeseries = timeseries_from_data(data=data, units=units)

    font = load_font("Roboto-Medium.ttf")

    template = """<layout>
    {example}
    </layout>"""

    with renderer.open() as map_renderer:
        for filepath in examples:
            print(filepath)
            with open(filepath) as f:
                example_markdown = f.read()

            count = 0

            basename = Path(os.path.basename(filepath))

            example_dest = os.path.join(dest, basename.stem)

            while True:
                match = re.search(r"{{(.+?)}}", example_markdown, re.MULTILINE | re.DOTALL)
                if match is None:
                    break

                imagename = basename.with_name(basename.stem + f"-{count}" + basename.suffix).with_suffix(f".png")
                count += 1

                group = match.group(1)
                xml = group.strip()
                example_markdown = example_markdown[0:match.start(0)] + \
                                   f"""
```xml
{xml}
```
<kbd>![{imagename}]({imagename})</kbd>
""" + \
                                   example_markdown[match.end(0):]

                layout = layout_from_xml(
                    template.format(example=xml),
                    map_renderer,
                    timeseries,
                    font,
                    privacy=NoPrivacyZone()
                )

                overlay = Overlay(dimensions_for(filepath), timeseries=timeseries, create_widgets=layout)
                image = overlay.draw(timeseries.min + (timeseries.max - timeseries.min))

                os.makedirs(example_dest, exist_ok=True)

                output_path = os.path.join(example_dest, imagename)
                image.save(fp=output_path)

            example_markdown = AUTO_HEADER + example_markdown

            with open(os.path.join(example_dest, "README.md"), "w") as f:
                f.write(example_markdown)


    def link(filename):
        stem = Path(filename).stem
        return f"[{stem}]({stem}/README.md)"


    links = "\n\n".join(
        [link(os.path.basename(filepath)) for filepath in examples]
    )

    with open(os.path.join(dest, "README.md"), "w") as f:
        f.write(f"""
{AUTO_HEADER}
# Layout Configuration Documentation

{ links }
        """)
