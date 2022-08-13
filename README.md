# Overlaying Dashboard onto GoPro MP4 Files

![GitHub Discussions](https://img.shields.io/github/discussions/time4tea/gopro-dashboard-overlay?style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/gopro-overlay?style=for-the-badge)


Discuss on [GitHub Discussions](https://github.com/time4tea/gopro-dashboard-overlay/discussions)

- Overlaying exciting graphics
- Support multiple resolutions, most GoPro models, normal, timelapse & timewarp modes
- Convert GoPro movie metadata to GPX or CSV files
- Cut sections from GoPro movies (including metadata)
- Join multiple GoPro files together (including metadata)

## Examples

![Example Dashboard Image](examples/2022-05-15-example.png)
![Example Dashboard Image](examples/2022-06-11-contrib-example.png)
![Example Dashboard Image](examples/2022-07-19-contrib-example-plane.jpg)

## Map Styles

Almost 30 different map styles are supported! - See [map styles](docs/maps/README.md) for more

*Example*

| .                                   | .                                             | .                                                     | .                                                     |
|-------------------------------------|-----------------------------------------------|-------------------------------------------------------|-------------------------------------------------------|
| ![osm](docs/maps/map_style_osm.png) | ![tf-cycle](docs/maps/map_style_tf-cycle.png) | ![tf-transport](docs/maps/map_style_tf-transport.png) | ![tf-landscape](docs/maps/map_style_tf-landscape.png) |


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

- The Roboto font needs to be installed on your system. You could install it with one of the following commands maybe.

```bash
pacman -S ttf-roboto
apt install truetype-roboto
apt install fonts-roboto
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

Please also see [PERFORMANCE.md](PERFORMANCE.md)

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

## Related Software

- https://github.com/julesgraus/interactiveGoProDashboardTool - An interactive helper to build the command line for the dashboard program

## Known Bugs / Issues

- Only tested on a GoPro Hero 9, that's all I have. Sample files for other devices are welcomed.

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

If you find any issues with new releases, please discuss in [GitHub Discussions](https://github.com/time4tea/gopro-dashboard-overlay/discussions)

- 0.58.0 Chart component now has configurable colours and size - see [docs/xml/examples/07-chart](docs/xml/examples/07-chart)
- 0.57.0 Experimental support for non-real-time (timelapse/timewarp) videos
  - Thanks to [@ptanov](https://github.com/ptanov)
- 0.56.0 Remove possible divide by zero error - only likely in timewarp/timelapse videos - I think
  - Minor changes to ffmpeg code, should have no visible effect
- 0.55.0 Huge improvement to View performance - used in chart - now charts with short windows are useable.
- 0.54.0 Fix [#60](https://github.com/time4tea/gopro-dashboard-overlay/issues/60) h/t [@remintz](https://github.com/remintz)
  - Some (older?) camera's don't have ORIN in ACCL and GYRO streams, so use a default
- 0.53.0 New feature for a frame - fade out to edge - see [docs](docs/xml/examples/09-frame) - thanks [@ptanov](https://github.com/ptanov)
  - Fix to GPX file loading - also, thanks [@ptanov](https://github.com/ptanov)
- 0.52.0 Update gopro-to-gpx.py to allow smaller GPX files (see help)
- 0.51.0 Fix [#52](https://github.com/time4tea/gopro-dashboard-overlay/issues/52) h/t [@danfossi](https://github.com/danfossi)
  - Support for Hero 8 Black ORIN spec zxY
- 0.50.0 Print installed version at program startup
- 0.49.0 Parsing & Display of Acceleration Information!
  - Major new functionality to parse and display acceleration data
  - Use metrics `accl.x` `accl.y` and `accl.z` in any widget or metric text
  - New component `bar` - see [bar docs](docs/xml/examples/07-bar)
  - Updated chart can now chart (probably) any metric - see [chart docs](docs/xml/examples/07-chart)
- 0.48.0 Fix [#48](https://github.com/time4tea/gopro-dashboard-overlay/issues/48) - h/t [@osresearch](https://github.com/osresearch)  
  - allow 'km' units where appropriate
- 0.47.0 Fix [#47](https://github.com/time4tea/gopro-dashboard-overlay/issues/47) - h/t [@osresearch](https://github.com/osresearch)  
  - using --layout-xml abc on the command line now implies --layout xml
  - Fix [#31](https://github.com/time4tea/gopro-dashboard-overlay/issues/31) h/t [@tve](https://github.com/tve)
  - When alt isn't available, don't blow up trying to calculate gradient
- 0.46.0 New component `compass-arrow` - see layout docs [examples](docs/xml/examples/README.md)
  - progress on support of time-lapse and time-warp files, but they don't work properly yet
  - built-in layout for 2.7k files
- 0.45.0 New Program `gopro-rename.py` - turn idiosyncratically named gopro files GX0100123.MP4 into 20220405-123416-london-england.MP4 using either provided description,
  - or looks up the location from the GPS, and makes file name from that.
  - uses the GPS timestamp to determine the time of the file. 
  - now gopro files will sort properly in your file viewer
  - also works around gopro camera drift, clock is always wrong.
  - can rename whole folders of files 

Older changes are in [CHANGELOG.md](CHANGELOG.md)

