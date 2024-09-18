#!/usr/bin/env python3
import datetime
import sys, os
from importlib import metadata
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Optional

from gopro_overlay import timeseries_process, gpmd_filters
from gopro_overlay.arguments import gopro_dashboard_arguments
from gopro_overlay.assertion import assert_file_exists
from gopro_overlay.buffering import SingleBuffer, DoubleBuffer
from gopro_overlay.common import temp_file_name
from gopro_overlay.config import Config
from gopro_overlay.counter import ReasonCounter
from gopro_overlay.date_overlap import DateRange
from gopro_overlay.dimensions import dimension_from
from gopro_overlay.execution import InProcessExecution
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro
from gopro_overlay.ffmpeg_overlay import FFMPEGNull, FFMPEGOverlay, FFMPEGOverlayVideo
from gopro_overlay.ffmpeg_profile import load_ffmpeg_profile
from gopro_overlay.font import load_font
from gopro_overlay.framemeta_gpx import merge_gpx_with_gopro, timeseries_to_framemeta
from gopro_overlay.geo import MapRenderer, api_key_finder, MapStyler
from gopro_overlay.gpmf import GPS_FIXED_VALUES, GPSFix
from gopro_overlay.layout import Overlay, speed_awareness_layout
from gopro_overlay.layout_xml import layout_from_xml, load_xml_layout, Converters
from gopro_overlay.loading import load_external, GoproLoader
from gopro_overlay.log import log, fatal
from gopro_overlay.point import Point
from gopro_overlay.privacy import PrivacyZone, NoPrivacyZone
from gopro_overlay.progresstrack import ProgressBarProgress
from gopro_overlay.timeunits import timeunits, Timeunit
from gopro_overlay.timing import PoorTimer, Timers
from gopro_overlay.units import units
from gopro_overlay.widgets.profile import WidgetProfiler


def accepter_from_args(include, exclude):
    if include and exclude:
        raise ValueError("Can't use both include and exclude at the same time")

    if include:
        return lambda n: n in include
    if exclude:
        return lambda n: n not in exclude

    return lambda n: True


def create_desired_layout(dimensions, layout, layout_xml: Path, include, exclude, renderer, timeseries, font,
                          privacy_zone, profiler, converters: Converters):
    accepter = accepter_from_args(include, exclude)

    if layout_xml:
        layout = "xml"

    if layout == "default":
        resource_name = Path(f"default-{dimensions.x}x{dimensions.y}")
        try:
            return layout_from_xml(
                load_xml_layout(resource_name), renderer, timeseries, font, privacy_zone, include=accepter,
                decorator=profiler, converters=converters
            )
        except FileNotFoundError:
            raise IOError(f"Unable to locate bundled layout resource: {resource_name}. "
                          f"You may need to create a custom layout for this frame size") from None

    elif layout == "speed-awareness":
        return speed_awareness_layout(renderer, font=font)
    elif layout == "xml":
        return layout_from_xml(
            load_xml_layout(layout_xml), renderer, timeseries, font, privacy_zone, include=accepter,
            decorator=profiler, converters=converters, xml_path=os.path.abspath(layout_xml)
        )
    else:
        raise ValueError(f"Unsupported layout {args.layout_creator}")


def fmtdt(dt: datetime.datetime):
    return dt.replace(microsecond=0).isoformat()


if __name__ == "__main__":

    args = gopro_dashboard_arguments()

    try:
        version = metadata.version("gopro_overlay")
    except PackageNotFoundError:
        version = "local"

    log(f"Starting gopro-dashboard version {version}")

    ffmpeg_exe = FFMPEG(location=args.ffmpeg_dir, print_cmds=args.show_ffmpeg)

    if not ffmpeg_exe.is_installed():
        log("Can't start ffmpeg - is it installed?")
        exit(1)
    if not ffmpeg_exe.libx264_is_installed():
        log("ffmpeg doesn't seem to handle libx264 files - it needs to be compiled with support for this, "
            "check your installation")
        exit(1)

    try:
        log(f"ffmpeg version is {ffmpeg_exe.version()}")
    except ValueError:
        log("ffmpeg version is unknown")

    log(f"Using Python version {sys.version}")
    if sys.version_info < (3, 10):
        log("*** Python version below 3.10 is not supported, please use supported version of Python")

    try:
        font = load_font(args.font)
    except OSError:
        fatal(f"Unable to load font '{args.font}' - use --font to choose a font that is installed.")

    ffmpeg_gopro = FFMPEGGoPro(ffmpeg_exe)

    # need in this scope for now
    inputpath: Optional[Path] = None
    generate = args.generate

    config_dir = args.config_dir
    config_dir.mkdir(exist_ok=True)

    config_loader = Config(config_dir)

    cache_dir = args.cache_dir
    cache_dir.mkdir(exist_ok=True)

    timers = Timers(printing=args.print_timings)

    try:
        with timers.timer("program"):
            with timers.timer("loading timeseries"):

                if args.use_gpx_only:

                    start_date: Optional[datetime.datetime] = None
                    end_date: Optional[datetime.datetime] = None
                    duration: Optional[Timeunit] = None

                    if args.input:
                        inputpath = assert_file_exists(args.input)

                        recording = ffmpeg_gopro.find_recording(inputpath)
                        dimensions = recording.video.dimension

                        duration = recording.video.duration

                        fns = {
                            "file-created": lambda f: f.ctime,
                            "file-modified": lambda f: f.mtime,
                            "file-accessed": lambda f: f.atime
                        }

                        if args.video_time_start:
                            start_date = fns[args.video_time_start](recording.file)
                            end_date = start_date + duration.timedelta()

                        if args.video_time_end:
                            start_date = fns[args.video_time_end](recording.file) - duration.timedelta()
                            end_date = start_date + duration.timedelta()

                    else:
                        generate = "overlay"

                    external_file: Path = assert_file_exists(args.gpx)
                    fit_or_gpx_timeseries = load_external(external_file, units)

                    log(f"GPX/FIT file:     {fmtdt(fit_or_gpx_timeseries.min)} -> {fmtdt(fit_or_gpx_timeseries.max)}")

                    # Give a bit of information here about what is going on
                    if start_date is not None:
                        log(f"Video File Dates: {fmtdt(start_date)} -> {fmtdt(end_date)}")

                        overlap = DateRange(start=start_date, end=end_date).overlap_seconds(
                            DateRange(start=fit_or_gpx_timeseries.min, end=fit_or_gpx_timeseries.max)
                        )

                        if overlap == 0:
                            fatal(
                                "Video file and GPX/FIT file don't overlap in time -  See "
                                "https://github.com/time4tea/gopro-dashboard-overlay/tree/main/docs/bin#create-a-movie"
                                "-from-gpx-and-video-not-created-with-gopro"
                            )

                    frame_meta = timeseries_to_framemeta(
                        fit_or_gpx_timeseries,
                        units,
                        start_date=start_date,
                        duration=duration
                    )
                    video_duration = frame_meta.duration()
                    packets_per_second = 10
                else:
                    inputpath = assert_file_exists(args.input)

                    counter = ReasonCounter()

                    loader = GoproLoader(
                        ffmpeg_gopro=ffmpeg_gopro,
                        units=units,
                        flags=args.load,
                        gps_lock_filter=gpmd_filters.standard(
                            dop_max=args.gps_dop_max,
                            speed_max=units.Quantity(args.gps_speed_max, args.gps_speed_max_units),
                            bbox=args.gps_bbox_lon_lat,
                            report=counter.because
                        )
                    )

                    gopro = loader.load(inputpath)

                    gpmd_filters.poor_report(counter)

                    frame_meta = gopro.framemeta

                    dimensions = gopro.recording.video.dimension
                    video_duration = gopro.recording.video.duration
                    packets_per_second = frame_meta.packets_per_second()

                    if len(frame_meta) == 0:
                        log("No GPS Information found in the Video - Was GPS Recording enabled?")
                        log("If you have a GPX File, See https://github.com/time4tea/gopro-dashboard-overlay/tree/main"
                            "/docs/bin#create-a-movie-from-gpx-and-video-not-created-with-gopro")
                        exit(1)

                    if args.gpx:
                        external_file: Path = args.gpx
                        fit_or_gpx_timeseries = load_external(external_file, units)
                        log(f"GPX/FIT file:     {fmtdt(fit_or_gpx_timeseries.min)} -> {fmtdt(fit_or_gpx_timeseries.max)}")
                        overlap = DateRange(start=frame_meta.date_at(frame_meta.min),
                                            end=frame_meta.date_at(frame_meta.max)).overlap_seconds(
                            DateRange(start=fit_or_gpx_timeseries.min, end=fit_or_gpx_timeseries.max)
                        )

                        if overlap == 0:
                            fatal(
                                "Video file and GPX/FIT file don't overlap in time -  See "
                                "https://github.com/time4tea/gopro-dashboard-overlay/tree/main/docs/bin#create-a-movie"
                                "-from-gpx-and-video-not-created-with-gopro")

                        log(f"GPX/FIT Timeseries has {len(fit_or_gpx_timeseries)} data points.. merging...")
                        merge_gpx_with_gopro(fit_or_gpx_timeseries, frame_meta, mode=args.gpx_merge)

                if args.overlay_size:
                    dimensions = dimension_from(args.overlay_size)

            if len(frame_meta) < 1:
                fatal(f"Unable to load GoPro metadata from {inputpath}. Use --debug-metadata to see more information")

            log(f"Generating overlay at {dimensions}")
            log(f"Timeseries has {len(frame_meta)} data points")
            log("Processing....")

            with timers.timer("processing"):
                locked_2d = lambda e: e.gpsfix in GPS_FIXED_VALUES
                locked_3d = lambda e: e.gpsfix == GPSFix.LOCK_3D.value

                frame_meta.process(timeseries_process.process_ses("point", lambda i: i.point, alpha=0.45),
                                   filter_fn=locked_2d)
                frame_meta.process_deltas(timeseries_process.calculate_speeds(), skip=packets_per_second * 3,
                                          filter_fn=locked_2d)
                frame_meta.process(timeseries_process.calculate_odo(), filter_fn=locked_2d)
                frame_meta.process_accel(timeseries_process.calculate_accel(), skip=18 * 3)
                frame_meta.process_deltas(timeseries_process.calculate_gradient(), skip=packets_per_second * 3,
                                          filter_fn=locked_3d)  # hack
                frame_meta.process(timeseries_process.process_kalman("speed", lambda e: e.speed))
                frame_meta.process(timeseries_process.filter_locked())

                frame_meta.process(timeseries_process.custom_passthrough())

            # privacy zone applies everywhere, not just at start, so might not always be suitable...
            if args.privacy:
                lat, lon, km = args.privacy.split(",")
                privacy_zone = PrivacyZone(
                    Point(float(lat), float(lon)),
                    units.Quantity(float(km), units.km)
                )
            else:
                privacy_zone = NoPrivacyZone()

            with MapRenderer(
                    cache_dir=cache_dir,
                    styler=MapStyler(
                        api_key_finder=api_key_finder(config_loader, args)
                    )
            ).open(args.map_style) as renderer:

                if args.profiler:
                    profiler = WidgetProfiler()
                else:
                    profiler = None

                if args.profile:
                    ffmpeg_options = load_ffmpeg_profile(config_loader, args.profile)
                else:
                    ffmpeg_options = None

                if args.show_ffmpeg:
                    redirect = None
                else:
                    redirect = temp_file_name(suffix=".txt")
                    log(f"FFMPEG Output is in {redirect}")

                execution = InProcessExecution(redirect=redirect)

                output: Path = args.output

                if generate == "none":
                    ffmpeg = FFMPEGNull()
                elif generate == "overlay":
                    output.unlink(missing_ok=True)
                    ffmpeg = FFMPEGOverlay(
                        ffmpeg=ffmpeg_exe,
                        output=output,
                        options=ffmpeg_options,
                        overlay_size=dimensions,
                        execution=execution,
                        creation_time=frame_meta.date_at(frame_meta.min)
                    )
                else:
                    output.unlink(missing_ok=True)
                    ffmpeg = FFMPEGOverlayVideo(
                        ffmpeg=ffmpeg_exe,
                        input=inputpath,
                        output=output,
                        options=ffmpeg_options,
                        overlay_size=dimensions,
                        execution=execution,
                        creation_time=frame_meta.date_at(frame_meta.min)
                    )

                draw_timer = PoorTimer("drawing frames")

                # Draw an overlay frame every 0.1 seconds of video
                timelapse_correction = frame_meta.duration() / video_duration
                log(f"Timelapse Factor = {timelapse_correction:.3f}")
                stepper = frame_meta.stepper(timeunits(seconds=0.1 * timelapse_correction))
                progress = ProgressBarProgress("Render")

                unit_converters = Converters(
                    speed_unit=args.units_speed,
                    distance_unit=args.units_distance,
                    altitude_unit=args.units_altitude,
                    temperature_unit=args.units_temperature,
                )

                layout_creator = create_desired_layout(
                    layout=args.layout,
                    layout_xml=args.layout_xml,
                    dimensions=dimensions,
                    include=args.include,
                    exclude=args.exclude,
                    renderer=renderer,
                    timeseries=frame_meta,
                    font=font,
                    privacy_zone=privacy_zone,
                    profiler=profiler,
                    converters=unit_converters
                )

                overlay = Overlay(framemeta=frame_meta, create_widgets=layout_creator)

                try:
                    progress.start(len(stepper))
                    with ffmpeg.generate() as writer:

                        if args.double_buffer:
                            log("*** NOTE: Double Buffer mode is experimental. It is believed to work fine on Linux. "
                                "Please raise issues if you see it working or not-working. Thanks ***")
                            buffer = DoubleBuffer(dimensions, args.bg, writer)
                        else:
                            buffer = SingleBuffer(dimensions, args.bg, writer)

                        with buffer:
                            for index, dt in enumerate(stepper.steps()):
                                progress.update(index)
                                draw_timer.time(lambda: buffer.draw(lambda frame: overlay.draw(dt, frame)))

                    log("Finished drawing frames. waiting for ffmpeg to catch up")
                    progress.complete()

                finally:
                    for t in [draw_timer]:
                        log(t)

                    if profiler:
                        log("\n\n*** Widget Timings ***")
                        profiler.print()
                        log("***\n\n")

    except KeyboardInterrupt:
        log("User interrupted...")
