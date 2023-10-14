import os
from itertools import zip_longest
from pathlib import Path

from gopro_overlay import geo, arguments
from gopro_overlay.config import Config
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg_gopro import MetaMeta
from gopro_overlay.font import load_font
from gopro_overlay.framemeta import framemeta_from_datafile
from gopro_overlay.geo import MapRenderer, ConfigKeyFinder, attrs_for_style, MapStyler
from gopro_overlay.layout import Overlay
from gopro_overlay.layout_xml import layout_from_xml
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.units import units
from gopro_overlay.widgets.widgets import SimpleFrameSupplier

mydir = os.path.dirname(__file__)

AUTO_HEADER = "<!-- \n\nAuto Generated File DO NOT EDIT \n\n-->\n"


def grouper(iterable, n, *, incomplete='fill', fillvalue=None):
    """Collect data into non-overlapping fixed-length chunks or blocks"""
    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    if incomplete == 'fill':
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == 'strict':
        return zip(*args, strict=True)
    if incomplete == 'ignore':
        return zip(*args)
    else:
        raise ValueError('Expected fill, strict, or ignore')


if __name__ == "__main__":
    dest = os.path.join(os.path.dirname(mydir), "docs/maps")

    datapath = os.path.join(mydir, "..", "tests/meta/gopro-meta.gpmd")
    framemeta = framemeta_from_datafile(
        datapath=datapath,
        units=units,
        metameta=MetaMeta(stream=3, frame_count=707, timebase=1000, frame_duration=1001)
    )

    font = load_font("Roboto-Medium.ttf")

    config_loader = Config(arguments.default_config_location)

    for style in geo.available_map_styles():
        print(style)

        renderer = MapRenderer(
            cache_dir=arguments.default_config_location,
            styler=MapStyler(api_key_finder=ConfigKeyFinder(loader=config_loader))
        )

        with renderer.open(style) as map_renderer:
            xml = """
                <layout>
                    <frame width="256" height="256" outline="0,0,0" cr="30">
                        <component type="moving_map" name="moving_map" size="256" zoom="11"/>
                        <component x="10" y="220" type="text">map style: {style}</component>
                    </frame>
                </layout>
            """.replace("{style}", style)

            layout = layout_from_xml(
                xml,
                map_renderer,
                framemeta,
                font,
                privacy=NoPrivacyZone()
            )

            overlay = Overlay(framemeta=framemeta, create_widgets=layout)
            supplier = SimpleFrameSupplier(Dimension(256, 256))
            image = overlay.draw(framemeta.min + (framemeta.max - framemeta.min), supplier.drawing_frame())

            imagename = f"map_style_{style}.png"

            os.makedirs(dest, exist_ok=True)
            output_path = os.path.join(dest, imagename)
            image.save(fp=output_path)

    attributions = {}

    for style in geo.available_map_styles():
        attrs = attrs_for_style(style)
        attributions[attrs["name"]] = attrs["attribution"]

    attribution = "\n\n".join([f"### {k} \n {v}" for k, v in attributions.items()])

    links = [f"![{style}](map_style_{style}.png)" for style in geo.available_map_styles()]
    lines = grouper(links, 4, fillvalue="")
    cells = [f"| {l[0]} | {l[1]} | {l[2]} | {l[3]} |" for l in lines]

    md_content = (Path(__file__).parent / "map-styles.md").read_text()

    md_content = AUTO_HEADER + md_content
    md_content = md_content.replace("{{ table }}", "\n".join(cells))
    md_content = md_content.replace("{{ attribution }}", attribution)

    (Path(dest) / "README.md").write_text(md_content)
