#!/usr/bin/env python3

import os
from pathlib import Path

import progressbar

from gopro_overlay import timeseries_process, progress_frames
from gopro_overlay.arguments import gopro_dashboard_arguments
from gopro_overlay.common import temp_file_name
from gopro_overlay.dimensions import dimension_from
from gopro_overlay.execution import InProcessExecution, ThreadingExecution
from gopro_overlay.ffmpeg import FFMPEGOverlay, FFMPEGGenerate, ffmpeg_is_installed, ffmpeg_libx264_is_installed, \
    find_streams, FFMPEGNull
from gopro_overlay.ffmpeg_profile import load_ffmpeg_profile
from gopro_overlay.font import load_font
from gopro_overlay.framemeta import framemeta_from
from gopro_overlay.framemeta_gpx import merge_gpx_with_gopro
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.gpx import load_timeseries
from gopro_overlay.layout import Overlay, speed_awareness_layout
from gopro_overlay.layout_xml import layout_from_xml, load_xml_layout
from gopro_overlay.point import Point
from gopro_overlay.privacy import PrivacyZone, NoPrivacyZone
from gopro_overlay.timeunits import timeunits
from gopro_overlay.timing import PoorTimer
from gopro_overlay.units import units

ourdir = Path.home().joinpath(".gopro-graphics")


def accepter_from_args(include, exclude):
    if include and exclude:
        raise ValueError("Can't use both include and exclude at the same time")

    if include:
        return lambda n: n in include
    if exclude:
        return lambda n: n not in exclude

    return lambda n: True


def create_desired_layout(dimensions, layout, layout_xml, include, exclude, renderer, timeseries, font, privacy_zone):
    accepter = accepter_from_args(include, exclude)

    if layout == "default":
        resource_name = f"default-{dimensions.x}x{dimensions.y}"
        try:
            return layout_from_xml(load_xml_layout(resource_name), renderer, timeseries, font, privacy_zone,
                                   include=accepter)
        except FileNotFoundError:
            raise IOError(f"Unable to locate bundled layout resource: {resource_name}. "
                          f"You may need to create a custom layout for this frame size") from None

    elif layout == "speed-awareness":
        return speed_awareness_layout(renderer, font=font)
    elif layout == "xml":
        return layout_from_xml(load_xml_layout(layout_xml), renderer, timeseries, font, privacy_zone, include=accepter)
    else:
        raise ValueError(f"Unsupported layout {args.layout}")


if __name__ == "__main__":

    args = gopro_dashboard_arguments()

    if not ffmpeg_is_installed():
        print("Can't start ffmpeg - is it installed?")
        exit(1)
    if not ffmpeg_libx264_is_installed():
        print("ffmpeg doesn't seem to handle libx264 files - it needs to be compiled with support for this, "
              "check your installation")
        exit(1)

    font = load_font(args.font)

    input_file = args.input

    if not os.path.exists(input_file):
        print(f"{input_file}: not found")
        exit(1)

    stream_info = find_streams(input_file)
    dimensions = stream_info.video_dimension
    print(f"Input file has size {dimensions}")

    with PoorTimer("program").timing():

        with PoorTimer("loading timeseries").timing():
            gopro_frame_meta = framemeta_from(
                input_file,
                metameta=stream_info.meta,
                units=units
            )

        if len(gopro_frame_meta) < 1:
            raise IOError(
                f"Unable to load GoPro metadata from {input_file}. Use --debug-metadata to see more information")

        print(f"GoPro Timeseries has {len(gopro_frame_meta)} data points")

        if args.gpx:
            gpx_timeseries = load_timeseries(args.gpx, units)
            print(f"GPX Timeseries has {len(gpx_timeseries)} data points.. merging...")
            merge_gpx_with_gopro(gpx_timeseries, gopro_frame_meta)

        print("Processing....")
        with PoorTimer("processing").timing():
            gopro_frame_meta.process(timeseries_process.process_ses("point", lambda i: i.point, alpha=0.45))
            gopro_frame_meta.process_deltas(timeseries_process.calculate_speeds(), skip=18 * 3)
            gopro_frame_meta.process(timeseries_process.calculate_odo())
            gopro_frame_meta.process_deltas(timeseries_process.calculate_gradient(),
                                            skip=18 * 3)  # hack approx 18 frames/sec * 3 secs

        ourdir.mkdir(exist_ok=True)

        # privacy zone applies everywhere, not just at start, so might not always be suitable...
        if args.privacy:
            lat, lon, km = args.privacy.split(",")
            privacy_zone = PrivacyZone(
                Point(float(lat), float(lon)),
                units.Quantity(float(km), units.km)
            )
        else:
            privacy_zone = NoPrivacyZone()

        with CachingRenderer(style=args.map_style, api_key=args.map_api_key).open() as renderer:

            if args.overlay_size:
                dimensions = dimension_from(args.overlay_size)

            overlay = Overlay(
                dimensions=dimensions,
                framemeta=gopro_frame_meta,
                create_widgets=create_desired_layout(
                    layout=args.layout, layout_xml=args.layout_xml,
                    dimensions=dimensions,
                    include=args.include, exclude=args.exclude,
                    renderer=renderer, timeseries=gopro_frame_meta, font=font, privacy_zone=privacy_zone)
            )

            if args.generate == "none":
                ffmpeg = FFMPEGNull()
            elif args.output == "overlay":
                ffmpeg = FFMPEGGenerate(
                    output=args.output,
                    overlay_size=dimensions
                )
            else:
                redirect = None if args.show_ffmpeg else temp_file_name()

                if args.thread:
                    execution = ThreadingExecution(redirect=redirect)
                else:
                    execution = InProcessExecution(redirect=redirect)

                print(f"FFMPEG Output is in {redirect}")

                if args.profile:
                    ffmpeg_options = load_ffmpeg_profile(ourdir, args.profile)
                else:
                    ffmpeg_options = None

                ffmpeg = FFMPEGOverlay(
                    input=input_file,
                    output=args.output,
                    options=ffmpeg_options,
                    vsize=args.output_size,
                    overlay_size=dimensions,
                    execution=execution
                )

            write_timer = PoorTimer("writing to ffmpeg")
            byte_timer = PoorTimer("image to bytes")
            draw_timer = PoorTimer("drawing frames")

            # Draw an overlay frame every 0.1 seconds
            stepper = gopro_frame_meta.stepper(timeunits(seconds=0.1))
            progress = progressbar.ProgressBar(
                widgets=[
                    'Render: ',
                    progressbar.Counter(),
                    ' [', progressbar.Percentage(), '] ',
                    ' [', progress_frames.Rate(), '] ',
                    progressbar.Bar(), ' ', progressbar.ETA()
                ],
                poll_interval=2.0,
                max_value=len(stepper)
            )

            try:
                with ffmpeg.generate() as writer:
                    for index, dt in enumerate(stepper.steps()):
                        progress.update(index)
                        frame = draw_timer.time(lambda: overlay.draw(dt))
                        tobytes = byte_timer.time(lambda: frame.tobytes())
                        write_timer.time(lambda: writer.write(tobytes))
                print("Finished drawing frames. waiting for ffmpeg to catch up")
                progress.finish()

            except KeyboardInterrupt:
                print("...Stopping...")
                pass
            finally:
                for t in [byte_timer, write_timer, draw_timer]:
                    print(t)
