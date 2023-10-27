# Create video overlays from GoPro Videos or any GPX/FIT file

<a href="https://github.com/time4tea/gopro-dashboard-overlay/discussions"><img alt="GitHub Discussions" src="https://img.shields.io/github/discussions/time4tea/gopro-dashboard-overlay?style=for-the-badge"></a>
<a href="https://pypi.org/project/gopro-overlay/"><img alt="PyPI" src="https://img.shields.io/pypi/v/gopro-overlay?style=for-the-badge"></a>
<a href="https://hub.docker.com/r/overlaydash/gopro-dashboard-overlay"><img alt="Docker" src="https://img.shields.io/docker/v/overlaydash/gopro-dashboard-overlay?label=Docker&style=for-the-badge"></a>

Discuss on [GitHub Discussions](https://github.com/time4tea/gopro-dashboard-overlay/discussions)

- Overlaying exciting graphics onto GoPro videos with super-exact synchronization
- Create videos from any GPX or FIT file - no GoPro required
- Support multiple resolutions, most GoPro models, normal, timelapse & timewarp modes
- Support GPUs to create movies at up to 17x realtime
- Convert GoPro movie metadata to GPX or CSV files
- Cut sections from GoPro movies (including metadata)
- Linux, Mac, Windows!

## Examples

![Example Dashboard Image](examples/2022-05-15-example.png)
![Example Dashboard Image](examples/2022-06-11-contrib-example.png)
![Example Dashboard Image](examples/2022-07-19-contrib-example-plane.jpg)
![Example Dashboard Image](examples/2023-07-23-contrib-example-ski-pov.png)
![Example Dashboard Image](examples/2023-07-23-contrib-example-ski-drone.png)

An Example of 'overlay only' mode, which generates movies from GPX files
![Example Dashboard Image](examples/2022-11-24-gpx-only-overlay.png)

Example from [examples/layout](examples/layout)
![Example Dashboard Image](examples/layout/layout-cairo-2704x1520.png)

## Map Styles

Almost 30 different map styles are supported! - See [map styles](docs/maps/README.md) for more

*Example*

| .                                   | .                                             | .                                                     | .                                                     |
|-------------------------------------|-----------------------------------------------|-------------------------------------------------------|-------------------------------------------------------|
| ![osm](docs/maps/map_style_osm.png) | ![tf-cycle](docs/maps/map_style_tf-cycle.png) | ![tf-transport](docs/maps/map_style_tf-transport.png) | ![tf-landscape](docs/maps/map_style_tf-landscape.png) |


## Requirements

- Python3.10 (development is done on Python3.11)
- ffmpeg (you'll need the ffmpeg program installed)
- libraqm (needed by [Pillow](https://pypi.org/project/Pillow/))

## Installation

See below for Windows instructions.

Install locally using `pip`, or use the provided Docker image

Optional: Some widgets require the `cairo` library - which must be installed separately.

### Installing and running with docker

The docker image is a new thing and still a bit experimental... please file an issue if you find any problems.

The docker image contains all you need to get started, and uses a volume `/work/`, which we suggest you map to the current directory which can contain your GoPro
files. Note that the docker version doesn't support nvidia GPU extensions.

The most recent version on docker is: <a href="https://hub.docker.com/r/overlaydash/gopro-dashboard-overlay"><img alt="Docker" src="https://img.shields.io/docker/v/overlaydash/gopro-dashboard-overlay?label=Docker&style=for-the-badge"></a>

```shell
docker run -it -v "$(pwd):/work" overlaydash/gopro-dashboard-overlay:<version> <program> [args...]
```

e.g.

```shell
docker run -it -v "$(pwd):/work" overlaydash/gopro-dashboard-overlay:0.92.0 gopro-dashboard.py GH010122.MP4 render/docker.MP4
```

Files created by the program will be created with the same uid that owns the mapped directory.

You can use the `--cache-dir` and `--config-dir` command line arguments to configure where the cache and config dirs are,
thereby making it easier to use persistent mapped volumes.



### Installing and running with pip

```shell
python -m venv venv
venv/bin/pip install gopro-overlay
```

The Roboto font needs to be installed on your system. You could install it with one of the following commands maybe.

```bash
pacman -S ttf-roboto
apt install truetype-roboto
apt install fonts-roboto
```

#### (Optional) Installing pycairo

Optionally, install `pycairo`

```shell
venv/bin/pip install pycairo==1.23.0
```

You might need to install some system libraries - This is what the pycairo docs suggest: 

Ubuntu/Debian: `sudo apt install libcairo2-dev pkg-config python3-dev`

macOS/Homebrew: `brew install cairo pkg-config`


## Installation on Windows

I don't know very much about windows, so corrections to these instructions are welcomed.

### Installing Python

Get the Windows installer from https://www.python.org/downloads/windows/ - Install it. Suggest "add to PATH". 

## Installation

```shell
python3 -mvenv venv
venv/Scripts/pip install gopro-overlay
```

You'll also need to install ffmpeg, if you don't have it already. You can download this from https://www.gyan.dev/ffmpeg/builds/ - The "essential version" is OK.
Unzip this somewhere. The default might be something like: C:\Users\james\Downloads\ffmpeg-6.0-essentials_build

Windows might not have Roboto Font, so start with a standard windows font - on my Windows 11 box, Trebuchet is installed. 

In PowerShell...
```shell
Set-ExecutionPolicy Unrestricted -Scope Process
.\venv\Scripts\activate.ps1
python .\venv\Scripts\gopro-dashboard.py --font trebuc.ttf --ffmpeg C:\Users\james\Downloads\ffmpeg-6.0-essentials_build\ffmpeg-6.0-essentials_build\bin input.mp4 output.mp4
```

Configuration files will go into `%UserProfile%\.gopro-graphics`

On my (pretty quick) Windows 11 Box, I get 35 fps (=3.5x realtime) on 2.7k with CPU only, and about the same with GPU. 

I did get two errors running with GPU:
-   decoder->cvdl->cuvidCreateDecoder(&decoder->decoder, params) failed -> CUDA_ERROR_INVALID_VALUE: invalid argument
    - This was fixed by following insttructions in docs/bin/README.md (adding -threads parameter) 
-   The minimum required Nvidia driver for nvenc is 522.25 or newer
    - Needed to upgrade nvidia driver.

`--double-buffer` DOES NOT WORK on Windows - shame - I don't really know how to implement this on Windows.


### Example

For full instructions on all command lines see [docs/bin](docs/bin)

```shell
venv/bin/gopro-dashboard.py --gpx ~/Downloads/Morning_Ride.gpx --privacy 52.000,-0.40000,0.50 ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

## Caveats

The GPS track in Hero 9 seems to be very poor. If you supply a GPX file from a Garmin or whatever, the
program will use this instead for the GPS. Hero 11 GPS is much improved.

Privacy allows you to set a privacy zone. Various widgets will not draw points within that zone.

The data recorded in the GoPro video will uses GPS time, which (broadly) is UTC. The renderer will use your local
timezone to interpret this, and use the local timezone. This may produce strange results if you go on holiday somewhere,
but then render the files when you get back home! On linux you can use the TZ variable to change the timezone that's
used.

## Writeups

There's a great writeup of how to use the software to make an overlay from a GPX file at https://blog.cubieserver.de/2022/creating-gpx-overlay-videos-on-linux/
(Nov 2022)

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

For more details on how to select these, and an example of Nvidia GPU, please see [docs/bin/PERFORMANCE_GUIDE.md](docs/bin/PERFORMANCE_GUIDE.md)

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

- Only tested on a GoPro Hero 9/11, that's all I have. Sample files for other devices are welcomed.

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
- 0.108.0 [Fix] GPX/GoPro overlay date checking had been broken for a while. Thanks (very much) to [@IbnGit](https://github.com/IbnGit) for raising
- 0.107.0 [Feature] New units! - "spm" - steps per minute, and "pace" - see [metrics docs](docs/xml/examples/04-metrics/README.md) for full explanation Thanks [@SlippyJimmy](https://github.com/SlippyJimmy)
- 0.106.0 [Feature] New map style "cyclosm" - see: https://www.cyclosm.org/ - An OpenStreetmap for cycling - See map examples for more
- 0.105.0 [Behaviour Change]  Fix [#150](https://github.com/time4tea/gopro-dashboard-overlay/issues/150) cairo circuit map aspect raio is wrong. Thanks [@yuanduopeng](https://github.com/yuanduopeng) for raising.
- 0.104.0 [Fix] Honour cmdline arg `--show-ffmpeg`
- 0.103.0 [Feature] Initial Windows Support! See Windows Installation Instructions.
- 0.102.0 [Feature] Support for alternate GoPro Max ORIN. Indicate when no GPS information found in file. Thanks [@xiaoxin01](https://github.com/xiaoxin01), [@ilisparrow](https://github.com/ilisparrow)  
- 0.101.0 [Fix] Fix error when loading FIT files that had GPS Accuracy information. Thanks [@rpellerin](https://github.com/rpellerin) 
- 0.100.0 [Breaking] Don't load GRAV/ACCL/CORI by default - its slow
  - [Breaking] Use EXTEND mode for GPX, so only add in additional data items. Use `--gpx-merge OVERWRITE` to restore previous behaviour. Previously it was all-or-none for GPX, now can choose to add hr/cad/power to GPX track from GoPro.
- 0.99.0 [Internal Changes Only] No user-visible changes expected.
- 0.98.0 [Feature] Add configurable background colour with `--bg rgba` thanks to [@mishuha](https://github.com/mishuha) in discussion https://github.com/time4tea/gopro-dashboard-overlay/discussions/120 for the concept. 
- 0.97.0 [Feature] Add new map style "local" - which will connect to a tileserver running locally on port 8000. This may be useful if you want to use a completely custom map - like a hand drawn one.
  - For more details see: https://github.com/time4tea/gopro-dashboard-overlay/discussions/132 Thanks to [@mattghub1](https://github.com/mattghub1) for the concept. 

Older changes are in [CHANGELOG.md](CHANGELOG.md)

