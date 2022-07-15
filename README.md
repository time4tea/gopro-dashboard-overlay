# Overlaying Dashboard onto GoPro MP4 Files

[![Join the chat at https://gitter.im/gopro-dashboard-overlay/community](https://badges.gitter.im/gopro-dashboard-overlay/community.svg)](https://gitter.im/gopro-dashboard-overlay/community)

- Overlaying exciting graphics
- Convert GoPro movie metadata to GPX or CSV files
- Cut sections from GoPro movies (including metadata)
- Join multiple GoPro files together (including metadata)

## Examples

![Example Dashboard Image](examples/2022-05-15-example.png)
![Example Dashboard Image](examples/2022-06-11-contrib-example.png)

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

The dashboard is updated every 0.1 seconds, regardless of the frame rate of the video, so 10 frames/s in this chart 
means 1 second of video is processed in 1 second.

These indicative figures are from Ubuntu on Intel Core i7-6700K CPU @ 4.00GHz with NVIDIA GeForce GTX 750 Ti

| Performance Option    | Frames/s "null" | Frames/s normal | Frames/s --profile nvgpu |
|-----------------------|-----------------|-----------------|--------------------------|
| Default (python 3.8)  | ~30             | ~10             | ~21                      | 
| PyPy                  | ~27             |                 |                          |
| Default + Pillow SIMD | ~60             | ~10             | ~25                      |


### GPU

Using the `--profile` option you can get a lot of extra performance out of the software. Please see the section on 
FFMPEG profiles in [docs/bin](docs/bin)

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

Using the `--generate none` setting, which 


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
- 0.44.0 Add [PR#44](https://github.com/time4tea/gopro-dashboard-overlay/pull/34) for extracting GPMF to ndjson. Thanks [@gregbaker](https://github.com/gregbaker)
- 0.43.0 Support for [Geoapify](https://geoapify.com/) maps, as well as existing [Thunderforest](https://www.thunderforest.com/) and [OSM](https://www.openstreetmap.org/) 
  - Small improvements in API Key handling. See [map styles docs](docs/maps/README.md)
- 0.42.0 Experimental threading mode `--thread` which just sends data to ffmpeg on a background thread. 
  - The result of lots of experimentation on timing, but basically if the GPU is maxed out, that's a limiting factor.
  - This gets a marginal performance gain of about 0.2frames/s for me. Use `nvtop` to check the "ENC" load on the GPU. 
  - Demonstrate that on a `null` ffmpeg, we can generate about 60 overlay frames a second, or 6 seconds/second
- 0.41.0 Allow alpha channel in colours everywhere. This means all text, backgrounds etc can now specify alpha component for colours
  - See docs for text component for [example](docs/xml/examples/01-simple-text/README.md)
- 0.40.0 BIG CHANGE - Hopefully align metadata with video *much* better. Please please raise issues if there are problems.
  - This has been tested with GOPRO Hero 9 and GOPRO Hero 7 - which use two different timing schemes, and appears to work.
  - This changes the way that GPX metadata is aligned with the track, which should also make it better
  - This might change how points with large DOP are rendered... feedback welcomed about how to do this best
- 0.39.0 Fix [#29](https://github.com/time4tea/gopro-dashboard-overlay/issues/29)  
- 0.38.0 Fix [#30](https://github.com/time4tea/gopro-dashboard-overlay/issues/30) thanks @tve 
- 0.37.0
  - Added new component "Moving Journey Map", which displays the whole journey on a moving map. See [docs](docs/xml/examples/06-moving-journey-map/README.md)
    - Possible fix for [feature request](https://github.com/time4tea/gopro-dashboard-overlay/issues/16) 


Older changes are in [CHANGELOG.md](CHANGELOG.md)

