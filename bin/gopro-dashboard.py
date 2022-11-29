#!/usr/bin/env python3

from importlib import metadata
from pathlib import Path
from typing import Optional

import progressbar

from gopro_overlay import timeseries_process, progress_frames, gpx, fit
from gopro_overlay.arguments import gopro_dashboard_arguments
from gopro_overlay.common import temp_file_name
from gopro_overlay.dimensions import dimension_from
from gopro_overlay.execution import InProcessExecution, ThreadingExecution
from gopro_overlay.ffmpeg import FFMPEGOverlayVideo, FFMPEGOverlay, ffmpeg_is_installed, ffmpeg_libx264_is_installed, \
    find_streams, FFMPEGNull
from gopro_overlay.ffmpeg_profile import load_ffmpeg_profile
from gopro_overlay.font import load_font
from gopro_overlay.framemeta import framemeta_from
from gopro_overlay.framemeta_gpx import merge_gpx_with_gopro, timeseries_to_framemeta
from gopro_overlay.geo import CachingRenderer, CompositeKeyFinder, ArgsKeyFinder, EnvKeyFinder, ConfigKeyFinder
from gopro_overlay.layout import Overlay, speed_awareness_layout
from gopro_overlay.layout_xml import layout_from_xml, load_xml_layout
from gopro_overlay.point import Point
from gopro_overlay.privacy import PrivacyZone, NoPrivacyZone
from gopro_overlay.timeseries import Timeseries
from gopro_overlay.timeunits import timeunits
from gopro_overlay.timing import PoorTimer
from gopro_overlay.units import units
from gopro_overlay.widgets.profile import WidgetProfiler

ourdir = Path.home().joinpath(".gopro-graphics")


def accepter_from_args(include, exclude):
    if include and exclude:
        raise ValueError("Can't use both include and exclude at the same time")

    if include:
        return lambda n: n in include
    if exclude:
        return lambda n: n not in exclude

    return lambda n: True


def create_desired_layout(dimensions, layout, layout_xml: Path, include, exclude, renderer, timeseries, font, privacy_zone, profiler):
    accepter = accepter_from_args(include, exclude)

    if layout_xml:
        layout = "xml"

    if layout == "default":
        resource_name = Path(f"default-{dimensions.x}x{dimensions.y}")
        try:
            return layout_from_xml(load_xml_layout(resource_name), renderer, timeseries, font, privacy_zone,
                                   include=accepter, decorator=profiler)
        except FileNotFoundError:
            raise IOError(f"Unable to locate bundled layout resource: {resource_name}. "
                          f"You may need to create a custom layout for this frame size") from None

    elif layout == "speed-awareness":
        return speed_awareness_layout(renderer, font=font)
    elif layout == "xml":
        return layout_from_xml(load_xml_layout(layout_xml), renderer, timeseries, font, privacy_zone, include=accepter, decorator=profiler)
    else:
        raise ValueError(f"Unsupported layout {args.layout}")


def load_external(filepath: Path, units) -> Timeseries:
    if filepath.suffix == ".gpx":
        return gpx.load_timeseries(filepath, units)
    elif filepath.suffix == ".fit":
        return fit.load_timeseries(filepath, units)
    else:
        raise IOError(f"Don't recognise filetype from {filepath} - support .gpx and .fit")


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

    # need in this scope for now
    inputpath: Optional[Path] = None
    generate = args.generate

    version = metadata.version("gopro_overlay")
    print(f"Starting gopro-dashboard version {version}")

    with PoorTimer("program").timing():

        with PoorTimer("loading timeseries").timing():

            if args.use_gpx_only:

                start_date = None
                duration = None

                if args.input:
                    inputpath = args.input
                    stream_info = find_streams(inputpath)
                    dimensions = stream_info.video.dimension

                    duration = stream_info.video.duration

                    fns = {
                        "file-created": lambda f: f.ctime,
                        "file-modified": lambda f: f.mtime,
                        "file-accessed": lambda f: f.atime
                    }

                    if args.video_time_start:
                        start_date = fns[args.video_time_start](stream_info.file)

                    if args.video_time_end:
                        start_date = fns[args.video_time_end](stream_info.file) - duration.timedelta()
                else:
                    generate = "overlay"

                external_file: Path = args.gpx
                frame_meta = timeseries_to_framemeta(load_external(external_file, units), units, start_date=start_date, duration=duration)
                video_duration = frame_meta.duration()
                packets_per_second = 1
            else:
                inputpath = args.input
                stream_info = find_streams(inputpath)

                if not stream_info.meta:
                    raise IOError(f"Unable to locate metadata stream in '{inputpath}' - is it a GoPro file")

                dimensions = stream_info.video.dimension
                video_duration = stream_info.video.duration
                packets_per_second = 18
                frame_meta = framemeta_from(inputpath, metameta=stream_info.meta, units=units)

                if args.gpx:
                    external_file: Path = args.gpx
                    gpx_timeseries = load_external(external_file, units)
                    print(f"GPX/FIT Timeseries has {len(gpx_timeseries)} data points.. merging...")
                    merge_gpx_with_gopro(gpx_timeseries, frame_meta)

            if args.overlay_size:
                dimensions = dimension_from(args.overlay_size)

        if len(frame_meta) < 1:
            raise IOError(f"Unable to load GoPro metadata from {inputpath}. Use --debug-metadata to see more information")

        print(f"Generating overlay at {dimensions}")
        print(f"Timeseries has {len(frame_meta)} data points")
        print("Processing....")

        with PoorTimer("processing").timing():
            frame_meta.process(timeseries_process.process_ses("point", lambda i: i.point, alpha=0.45))
            frame_meta.process_deltas(timeseries_process.calculate_speeds(), skip=packets_per_second * 3)
            frame_meta.process(timeseries_process.calculate_odo())
            frame_meta.process_deltas(timeseries_process.calculate_gradient(), skip=packets_per_second * 3)  # hack

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

        api_key_finder = CompositeKeyFinder(
            ArgsKeyFinder(args),
            EnvKeyFinder(),
            ConfigKeyFinder()
        )

        with CachingRenderer(style=args.map_style, api_key_finder=api_key_finder).open() as renderer:

            if args.profiler:
                profiler = WidgetProfiler()
            else:
                profiler = None

            if args.profile:
                ffmpeg_options = load_ffmpeg_profile(ourdir, args.profile)
            else:
                ffmpeg_options = None

            if args.show_ffmpeg:
                redirect = None
            else:
                redirect = temp_file_name()
                print(f"FFMPEG Output is in {redirect}")

            if args.thread:
                execution = ThreadingExecution(redirect=redirect)
            else:
                execution = InProcessExecution(redirect=redirect)

            if generate == "none":
                ffmpeg = FFMPEGNull()
            elif generate == "overlay":
                ffmpeg = FFMPEGOverlay(output=args.output, options=ffmpeg_options, overlay_size=dimensions, execution=execution)
            else:
                ffmpeg = FFMPEGOverlayVideo(input=inputpath, output=args.output, options=ffmpeg_options, vsize=args.output_size, overlay_size=dimensions, execution=execution)

            write_timer = PoorTimer("writing to ffmpeg")
            byte_timer = PoorTimer("image to bytes")
            draw_timer = PoorTimer("drawing frames")

            # Draw an overlay frame every 0.1 seconds of video
            timelapse_correction = frame_meta.duration() / video_duration
            print(f"Timelapse Factor = {timelapse_correction:.3f}")
            stepper = frame_meta.stepper(timeunits(seconds=0.1 * timelapse_correction))
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

            overlay = Overlay(
                dimensions=dimensions,
                framemeta=frame_meta,
                create_widgets=create_desired_layout(
                    layout=args.layout, layout_xml=args.layout_xml,
                    dimensions=dimensions,
                    include=args.include, exclude=args.exclude,
                    renderer=renderer, timeseries=frame_meta, font=font, privacy_zone=privacy_zone, profiler=profiler)
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

                if profiler:
                    print("\n\n*** Widget Timings ***")
                    profiler.print()
                    print("***\n\n")
