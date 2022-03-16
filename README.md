# Overlaying Dashboard onto GoPro MP4 Files

[![Join the chat at https://gitter.im/gopro-dashboard-overlay/community](https://badges.gitter.im/gopro-dashboard-overlay/community.svg)](https://gitter.im/gopro-dashboard-overlay/community)

- Overlaying exciting graphics
- Convert GoPro movie metadata to GPX or CSV files
- Cut sections from GoPro movies (including metadata)
- Join multiple GoPro files together (including metadata)

## Examples

![Example Dashboard Image](examples/2021-09-22-example.png)

## Requirements

- Python3.8
- ffmpeg (you'll need the ffmpeg program installed)
- Unixy machine (probably, untested on Windows)

## How to use

- Install with pip

```shell
python -m venv venv
venv/bin/pip install gopro-overlay
```

## Overlaying a dashboard

```shell
venv/bin/gopro-dashboard.py
```

The GPS track in Hero 9 (at least) seems to be very poor. If you supply a GPX file from a Garmin or whatever, the
program will use this instead for the GPS.

Privacy allows you to set a privacy zone. Various widgets will not draw points within that zone.

The data recorded in the GoPro video will uses GPS time, which (broadly) is UTC. The renderer will use your local
timezone to interpret this, and use the local timezone. This may produce strange results if you go on holiday somewhere,
but then render the files when you get back home! On linux you can use the TZ variable to change the timezone that's
used.

### Example

For full instructions on all command lines see [docs/bin](docs/bin)

```shell
venv/bin/gopro-dashboard.py --gpx ~/Downloads/Morning_Ride.gpx --privacy 52.000,-0.40000,0.50 ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

### Format of the Dashboard Configuration file

Several dashboards are built-in to the software, but the dashboard layout is highly configurable, controlled by an XML
file.

For more information on the (extensive) configurability of the layout please see [docs/xml](docs/xml) and lots
of [examples](docs/xml/examples/README.md)

## FFMPEG Control & GPUs

*Experimental*

FFMPEG has **a lot** of options! This program comes with some mostly sensible defaults, but to use GPUs and control the
output much more carefully, including framerates and bitrates, you can use a JSON file containing a number of 'profiles'
and select the profile you want when running the program.

For more details on how to select these, and an example of Nvidia GPU, please see [docs/bin](docs/bin)

## Converting to GPX files

```shell
venv/bin/gopro-to-gpx.py <input-file> [output-file]
```

## Joining a sequence of MP4 files together

Use the gopro-join.py command. Given a single file from the sequence, it will find and join together all the files. If
you have any problems with this, please do raise an issue - I don't have that much test data.

The joined file almost certainly won't work in the GoPro tools! - But it should work with `gopro-dashboard.py` - I will
look into the additional technical stuff required to make it work in the GoPro tools.

*This will require a lot of disk space!*

```shell
venv/bin/gopro-join.py /media/sdcard/DCIM/100GOPRO/GH030170.MP4 /data/gopro/nice-ride.MP4
```

## Cutting a section from a GoPro file

You can cut a section of the gopro file, with metadata.

## Performance

Performance isn't really a major goal... Right now it processes video just a bit faster than realtime, so your 10 minute
video will probably take about 10 minutes to render. This is highly dependent on your CPU though.

### Pillow-SIMD

You might be able to get some more performance out of the program by using pillow-simd. Installing it is a bit more
complicated. You'll need a compiler etc. Follow the installation instructions
at https://github.com/uploadcare/pillow-simd#pillow-simd

Short version:
```bash
venv/bin/pip uninstall pillow
venv/bin/pip install pillow-simd==8.3.2.post0
```
The frame drawing rate is quite a bit faster, but won't make a huge difference unless GPU settings are used with ffmpeg.

No tests are run in this project with pillow-simd, so output may vary (but their tests are good, so I wouldn't expect any huge differences, if any)


## Known Bugs / Issues

- Only tested on a GoPro Hero 9, that's all I have. Sample files for other devices are welcomed.
- Aligning overlay with video - not exact! - Start garmin first, and wait for GPS lock before recording

## Icons

Icon files in [icons](gopro_overlay/icons) are not covered by the MIT licence

## Map Data

Data © [OpenStreetMap contributors](http://www.openstreetmap.org/copyright)

Some Maps © [Thunderforest](http://www.thunderforest.com/)

## References

https://github.com/juanmcasillas/gopro2gpx

https://github.com/JuanIrache/gopro-telemetry

https://github.com/gopro/gpmf-parser

https://coderunner.io/how-to-compress-gopro-movies-and-keep-metadata/

## Other Related Software

https://github.com/progweb/gpx2video

https://github.com/JuanIrache/gopro-telemetry

## Latest Changes
- 0.35.0
  - Add `rotate` to `asi` component. see [docs](docs/xml/examples/07-air-speed-indicator)
  - Some refactoring (should have no visible effect)
- 0.34.0
  - Add new component `asi` - an Airspeed Indicator - see [docs](docs/xml/examples/07-air-speed-indicator)
- 0.33.0
  - Add *experimental* support for 'ffmpeg profiles' as documented above
- 0.32.0
    - Add option to disable rotation in moving map (thanks  [@SECtim](https://github.com/SECtim))
- 0.31.0
    - (Change in behaviour) Use input file framerate as output file framerate. This may make output files bigger.
        - A more comprehensive mechanism to control ffmpeg options is planned for a later release
- 0.30.0
    - Attempt to fix character encoding issues on Mac (can't test, as I don't have a Mac)
- 0.29.0
    - Add `compass` component (experimental!) - Draws a simple compass
    - Add `frame` component - Draws a clipping maybe-rounded box to contain other components.
    - Add initial docs for XML layout
- 0.28.0
    - Only rerender moving map if it has moved since last frame - will be much quicker under certain circumstances
    - Refactorings in how map border/opacity is rendered (should have no visible effect, maybe marginally faster)
- 0.27.0
    - Fix [Issue #20](https://github.com/time4tea/gopro-dashboard-overlay/issues/20) Minor improvement in GPX parsing.
      Hopefully more tolerant of GPX files that don't contain hr/cadence/temp extensions
- 0.26.0
    - (Change in behaviour) - Fix [Issue #17](https://github.com/time4tea/gopro-dashboard-overlay/issues/17) Will now
      use local timezone when rendering datetimes. (H/T [@tve](https://github.com/tve) )

Older changes are in [CHANGELOG.md](CHANGELOG.md)

