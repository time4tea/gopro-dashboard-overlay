# Programs Included

- [gopro-dashboard.py](#gopro-dashboardpy)
- [gopro-rename.py](#gopro-renamepy)
- [gopro-cut.py](#gopro-cutpy)
- [gopro-join.py](#gopro-joinpy)
- [gopro-to-csv.py](#gopro-to-csvpy)
- [gopro-to-gpx.py](#gopro-to-gpxpy)
- [gopro-contrib-data-extract.py](#gopro-contrib-data-extractpy)

# gopro-dashboard.py

Creates a dashboard overlaying your GoPro movie. Lots of options!

- Supports many different units - metres, miles, km..
- GPU support ( see [FFMPEG Profiles](#ffmpeg-profiles))
- Custom layouts
- Various different widgets (see [Widget Documentation](../xml/README.md))

## Basic Usage

*Create an overlay movie*

```shell
venv/bin/gopro-dashboard.py ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

*Create an overlay movie using a GPX file*

```shell
venv/bin/gopro-dashboard.py --gpx ~/Downloads/Morning_Ride.gpx ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

*Create a movie with a privacy zone*
```shell
venv/bin/gopro-dashboard.py --privacy 52.000,-0.40000,0.50 ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

*Create a movie with a custom layout*
```shell
venv/bin/gopro-dashboard.py --layout xml --layout-xml ~/layouts/my-layout.xml ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

*Create a movie with a specific map style*
```shell
venv/bin/gopro-dashboard.py --map-style tf-cycle --map-api-key my-api-key ~/layouts/my-layout.xml ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

*Create a transparent overlay without video, for using it in external software*

You'll need to create an overlay profile (with alpha channel) - see [Create a movie with alpha channel](#create-a-movie-with-alpha-channel-using-only-gpx-file-without-any-video-at-all)

```shell
venv/bin/gopro-dashboard.py --generate overlay ~/gopro/GH020073.MP4 GH020073-dashboard.mov
```

*Create a movie, using GPU encoding and decoding*

You'll need to create a profile - see [FFMPEG Profiles](#ffmpeg-profiles)

```shell
venv/bin/gopro-dashboard.py --profile nvgpu ~/layouts/my-layout.xml ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

## Units

The units for `speed`, `altitude`, `distance` and `temperature` can be controlled from the command line. 

```shell
venv/bin/gopro-dashboard.py --units-speed kph --units-altitude feet --units-temperature degreeF ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```

## Omitting Widgets

If the layout you are using has a widget you don't want, you can use `--include <name> <name>.. ` or `--exclude <name> <name>...`
on the command line to include or exclude that widget.  To get the name of the widget, currently you need to look at the xml file. (linked above)

## Skipping Containers

If you didn't want to render a container, you could add `--exclude <container-name>` when running the program, and this
container would be skipped.

## FFMPEG Profiles

Create a file `~/.gopro-graphics/ffmpeg-profiles.json`, and put FFMPEG parameters to control the `input` and `output`

Both `input` and `output` sections are mandatory.

The ffmpeg command line arguments are a bit of a minefield, so when using this, then it definitely is out-of-warranty. (There's no warranty anyway!)

Please consider contributing useful settings, particularly those that control GPU outputs.

```json
{
  "profile-name": {
    "input": ["list", "of", "input", "options"],
    "output": ["list", "of", "output", "options"]
  }
}
```

Example:

```json
{
  "nvgpu": {
    "input": ["-hwaccel", "nvdec"],
    "output": ["-vcodec", "h264_nvenc", "-rc:v", "cbr", "-b:v", "50000k", "-bf:v", "3", "-profile:v", "high", "-spatial-aq", "true"]
  },
  "low-fr": {
    "input": [],
    "output": ["-r", "10"]
  }
}
```

## Creating Videos using only GPX File

### Create a movie with alpha channel, using only GPX file, without any video at all

This is when you want to use external software to do the final video - combining the "dashboard" video and some other video using Lightworks
or whatever 

You'll need to create a profile - see [FFMPEG Profiles](#ffmpeg-profiles)

```json
{
  "overlay": {
    "input": [],
    "output": ["-vcodec", "png"]
  }
}
```

then execute (NOTE: extension is `mov`)

```shell
venv/bin/gopro-dashboard.py --gpx-only --gpx ~/Downloads/Morning_Ride.gpx --profile overlay --overlay-size 1920x1080 GH020073-dashboard.mov
```
if you use `-vcodec rawvideo` file will be really huge

or you can use slower codecs (but smaller file size) `vp9` or`vp8` (even slower) or `hevc_videotoolbox` (available on Mac only):

```json
{
  "overlay": {
    "input": [],
    "output": ["-vcodec", "vp9", "-pix_fmt", "yuva420p"]
  },
  "sloweroverlay": {
    "input": [],
    "output": ["-vcodec", "vp8", "-pix_fmt", "yuva420p", "-auto-alt-ref", "0"]
  }
}
```

then execute (NOTE: extension is `webm`)

```shell
venv/bin/gopro-dashboard.py --use-gpx-only --gpx ~/Downloads/Morning_Ride.gpx --profile overlay --overlay-size 1920x1080 GH020073-dashboard.webm
```

### Create a movie from GPX and video not created with GoPro

This is currently quite hard to align things properly!

#### Ensure file time matches GPX times

Make sure that the time of the file is correct and when aligned to the timezone of your computer matches the data in GPX file 
(this might not be the case if video is recorded abroad). 

If it is not correct you can fix it using `touch -d '2022-08-29T11:17:44Z' file.mp4`. 

To get the correct time you can try with different dates available from `exiftool file.mp4` or `exiftool thumbnail_image_of_the_video.thm` 
(if thumbnail image exist), from SRT/flight log viewer/CSV from Airdata, etc. 

But first make sure that you have set the correct date and time of the camera BEFORE recording the video.

```shell
venv/bin/gopro-dashboard.py --video-time-start file-accessed --use-gpx-only --gpx ~/Downloads/Morning_Drive.gpx ~/recording/drive.MP4 GH020073-dashboard.MP4
```

Depending on the camera maker and model `file-accessed`, `file-created`, `file-modified` should be used for `--video-time-start` or `--video-time-end`, e.g.

```shell
venv/bin/gopro-dashboard.py --video-time-end file-created --use-gpx-only  --gpx ~/Downloads/Morning_Ride.gpx ~/recording/flight.MP4 GH020073-dashboard.MP4
```

```shell
venv/bin/gopro-dashboard.py --video-time-end file-modified --use-gpx-only --gpx ~/Downloads/Morning_Ride.gpx ~/recording/sail.MP4 GH020073-dashboard.MP4
```


## GPU Learnings

### nvidia cuvidCreateDecoder failed

You might see this in the ffmpeg output:

```
[h264 @ 0x557b56012a00] decoder->cvdl->cuvidCreateDecoder(&decoder->decoder, params) failed -> CUDA_ERROR_INVALID_VALUE: invalid argument
[h264 @ 0x557b56012a00] Using more than 32 (34) decode surfaces might cause nvdec to fail.
[h264 @ 0x557b56012a00] Try lowering the amount of threads. Using 16 right now.
[h264 @ 0x557b56012a00] Failed setup for format cuda: hwaccel initialisation returned error.
[swscaler @ 0x557b57b570c0] deprecated pixel format used, make sure you did set range correctly
```

I 'fixed' this with this profile:

```json
{
  "nvgpu": {
    "input": ["-hwaccel", "nvdec", "-threads", "12"],
    "output": ["-vcodec", "h264_nvenc", "-rc:v", "cbr", "-b:v", "50000k", "-bf:v", "3", "-profile:v", "high", "-spatial-aq", "true"]
  }
}
```

I don't know the formula for calculating the correct number of threads... this was trial and error.


### Usage

```
usage: gopro-dashboard.py [-h] [--font FONT] [--gpx GPX] [--privacy PRIVACY] [--generate {default,overlay,none}]
                          [--overlay-size OVERLAY_SIZE] [--output-size OUTPUT_SIZE] [--profile PROFILE]
                          [--config-dir CONFIG_DIR] [--cache-dir CACHE_DIR] [--use-gpx-only]
                          [--video-time-start {file-created,file-modified,file-accessed}]
                          [--video-time-end {file-created,file-modified,file-accessed}]
                          [--map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas,geo-osm-carto,geo-osm-bright,geo-osm-bright-grey,geo-osm-bright-smooth,geo-klokantech-basic,geo-osm-liberty,geo-maptiler-3d,geo-toner,geo-toner-grey,geo-positron,geo-positron-blue,geo-positron-red,geo-dark-matter,geo-dark-matter-brown,geo-dark-matter-dark-grey,geo-dark-matter-dark-purple,geo-dark-matter-purple-roads,geo-dark-matter-yellow-roads}]
                          [--map-api-key MAP_API_KEY] [--layout {default,speed-awareness,xml}] [--layout-xml LAYOUT_XML]
                          [--exclude EXCLUDE [EXCLUDE ...]] [--include INCLUDE [INCLUDE ...]] [--units-speed UNITS_SPEED]
                          [--units-altitude UNITS_ALTITUDE] [--units-distance UNITS_DISTANCE]
                          [--units-temperature {kelvin,degC,degF}] [--gps-dop-max GPS_DOP_MAX]
                          [--gps-speed-max GPS_SPEED_MAX] [--gps-speed-max-units GPS_SPEED_MAX_UNITS]
                          [--gps-bbox-lon-lat GPS_BBOX_LON_LAT] [--show-ffmpeg] [--debug-metadata] [--profiler]
                          [input] output

Overlay gadgets on to GoPro MP4

positional arguments:
  input                 Input MP4 file - Optional with --use-gpx-only (default: None)
  output                Output Video File - MP4/MOV/WEBM all supported, see Profiles documentation

options:
  -h, --help            show this help message and exit
  --font FONT           Selects a font (default: Roboto-Medium.ttf)
  --gpx GPX, --fit GPX  Use GPX/FIT file for location / alt / hr / cadence / temp ... (default: None)
  --privacy PRIVACY     Set privacy zone (lat,lon,km) (default: None)
  --generate {default,overlay,none}
                        Type of output to generate (default: default)
  --overlay-size OVERLAY_SIZE
                        <XxY> e.g. 1920x1080 Force size of overlay. Use if video differs from supported bundled overlay
                        sizes (1920x1080, 3840x2160), Required if --use-gpx-only (default: None)
  --output-size OUTPUT_SIZE
                        Vertical size of output movie (default: 1080)
  --profile PROFILE     Use ffmpeg options profile <name> from ~/gopro-graphics/ffmpeg-profiles.json (default: None)
  --config-dir CONFIG_DIR
                        Location of config files (api keys, profiles, ...) (default: /home/richja/.gopro-graphics)
  --cache-dir CACHE_DIR
                        Location of caches (map tiles, ...) (default: /home/richja/.gopro-graphics)

GPX Only:
  Creating Movies from GPX File only

  --use-gpx-only, --use-fit-only
                        Use only the GPX/FIT file - no GoPro location data (default: False)
  --video-time-start {file-created,file-modified,file-accessed}
                        Use file dates for aligning video and GPS information, only when --use-gpx-only - EXPERIMENTAL! -
                        may be changed/removed (default: None)
  --video-time-end {file-created,file-modified,file-accessed}
                        Use file dates for aligning video and GPS information, only when --use-gpx-only - EXPERIMENTAL! -
                        may be changed/removed (default: None)

Mapping:
  Display of Maps

  --map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas,geo-osm-carto,geo-osm-bright,geo-osm-bright-grey,geo-osm-bright-smooth,geo-klokantech-basic,geo-osm-liberty,geo-maptiler-3d,geo-toner,geo-toner-grey,geo-positron,geo-positron-blue,geo-positron-red,geo-dark-matter,geo-dark-matter-brown,geo-dark-matter-dark-grey,geo-dark-matter-dark-purple,geo-dark-matter-purple-roads,geo-dark-matter-yellow-roads}
                        Style of map to render (default: osm)
  --map-api-key MAP_API_KEY
                        API Key for map provider, if required (default OSM doesn't need one) (default: None)

Layout:
  Controlling layout

  --layout {default,speed-awareness,xml}
                        Choose graphics layout (default: default)
  --layout-xml LAYOUT_XML
                        Use XML File for layout (default: None)
  --exclude EXCLUDE [EXCLUDE ...]
                        exclude named component (will include all others (default: None)
  --include INCLUDE [INCLUDE ...]
                        include named component (will exclude all others) (default: None)

Units:
  Controlling Units

  --units-speed UNITS_SPEED
                        Default unit for speed. Many units supported: mph, mps, kph, kph, knot, ... (default: mph)
  --units-altitude UNITS_ALTITUDE
                        Default unit for altitude. Many units supported: foot, mile, metre, meter, parsec, angstrom, ...
                        (default: metre)
  --units-distance UNITS_DISTANCE
                        Default unit for distance. Many units supported: mile, km, foot, nmi, meter, metre, parsec, ...
                        (default: mile)
  --units-temperature {kelvin,degC,degF}
                        Default unit for temperature (default: degC)

GPS:
  Controlling GPS Parsing (from GoPro Only)

  --gps-dop-max GPS_DOP_MAX
                        Max DOP - Points with greater DOP will be considered 'Not Locked' (default: 10)
  --gps-speed-max GPS_SPEED_MAX
                        Max GPS Speed - Points with greater speed will be considered 'Not Locked' (default: 60)
  --gps-speed-max-units GPS_SPEED_MAX_UNITS
                        Units for --gps-speed-max (default: kph)
  --gps-bbox-lon-lat GPS_BBOX_LON_LAT
                        Define GPS Bounding Box, anything outside will be considered 'Not Locked' -
                        minlon,minlat,maxlon,maxlat (default: None)

Debugging:
  Controlling debugging outputs

  --show-ffmpeg         Show FFMPEG output (not usually useful) (default: False)
  --debug-metadata      Show detailed information when parsing GoPro Metadata (default: False)
  --profiler            Do some basic profiling of the widgets to find ones that may be slow (default: False)
```

# gopro-extract.py

Extract GoPro metadata to its own file.

### Usage

```text
usage: gopro-extract.py [-h] input [output]

Extract GoPro metadata to data file

positional arguments:
  input       Input file
  output      Output file (default stdout)

optional arguments:
  -h, --help  show this help message and exit
```

# gopro-rename.py

Rename a GoPro file to a date-based filename, which means it will sort correctly by name in a file viewer.

The GoPro files have an unusual naming format with the chapter first, and the "event" second, so sorting by name
gives a strange ordering. Additionally, the GoPro files are dated with the on board "real-time-clock", but this is very inaccurate
and often wildy wrong. This program finds the first GPS-locked datetime in the metadata, and uses that for the filename.

Additionally, you can provide a "description" on the command line, and that will be incorporated into the file name

Additionally, you can specify that the program will look up the address of the GPS location, and it will name the files
according to that location:

### Usage

```text
usage: gopro-rename.py [-h] [-t] [-to] [--desc DESC] [--geo] [-y] [--dirs] file [file ...]

Rename a series of GoPro files by date. Does nothing (so its safe) by default.

positional arguments:
  file               The files to rename, or directory/ies containing files

options:
  -h, --help         show this help message and exit
  -t, --touch        change the modification time of the file
  -to, --touch-only  change the modification time of the file only - don't rename
  --desc DESC        a descriptive name to add to the filename - the filename will be yyyymmdd-hhmmss-{desc}.MP4
  --geo              [EXPERIMENTAL] Use Geocode.xyz to add description for you (city-state) - see https://geocode.xyz/pricing for terms
  -y, --yes          Rename the files, don't just print what would be done
  --dirs             Allow directory

```

# gopro-to-csv.py

Convert GoPro metadata to a CSV file.

Not hugely flexible at the moment.

### Usage

```text
usage: gopro-to-csv.py [-h] [--every EVERY] [--only-locked] [--gps-dop-max GPS_DOP_MAX] [--gps-speed-max GPS_SPEED_MAX] [--gps-speed-max-units GPS_SPEED_MAX_UNITS] [--gps-bbox-lon-lat GPS_BBOX_LON_LAT] [--gpx]
                       input [output]

Convert GoPro MP4 file / GPX File to CSV

positional arguments:
  input                 Input file
  output                Output CSV file (default stdout)

options:
  -h, --help            show this help message and exit
  --every EVERY         Output a point every 'n' seconds. Default is output all points (usually 20/s)
  --only-locked         Only output points where GPS is locked
  --gps-dop-max GPS_DOP_MAX
                        Max DOP - Points with greater DOP will be considered 'Not Locked'
  --gps-speed-max GPS_SPEED_MAX
                        Max GPS Speed - Points with greater speed will be considered 'Not Locked'
  --gps-speed-max-units GPS_SPEED_MAX_UNITS
                        Units for --gps-speed-max
  --gps-bbox-lon-lat GPS_BBOX_LON_LAT
                        Define GPS Bounding Box, anything outside will be considered 'Not Locked' - minlon,minlat,maxlon,maxlat
  --gpx                 Input is a gpx file

```

# gopro-to-gpx.py

Convert GoPro metadata to a GPX file for upload/import into other software

### Usage

```text
sage: gopro-to-gpx.py [-h] [--every EVERY] [--only-locked] [--gps-dop-max GPS_DOP_MAX] [--gps-speed-max GPS_SPEED_MAX] [--gps-speed-max-units GPS_SPEED_MAX_UNITS] [--gps-bbox-lon-lat GPS_BBOX_LON_LAT] input [output]

Convert GoPro MP4 file to GPX

positional arguments:
  input                 Input MP4 file
  output                Output GPX file (default stdout)

options:
  -h, --help            show this help message and exit
  --every EVERY         Output a point every 'n' seconds. Default is output all points (usually 20/s)
  --only-locked         Only output points where GPS is locked
  --gps-dop-max GPS_DOP_MAX
                        Max DOP - Points with greater DOP will be considered 'Not Locked'
  --gps-speed-max GPS_SPEED_MAX
                        Max GPS Speed - Points with greater speed will be considered 'Not Locked'
  --gps-speed-max-units GPS_SPEED_MAX_UNITS
                        Units for --gps-speed-max
  --gps-bbox-lon-lat GPS_BBOX_LON_LAT
                        Define GPS Bounding Box, anything outside will be considered 'Not Locked' - minlon,minlat,maxlon,maxlat

```

# gopro-join.py

Join a series of GoPro files to a single movie - including the metadata

### Usage

```text
usage: gopro-join.py [-h] input output

Concatenate sequence of GoPro Files

positional arguments:
  input       A single MP4 file from the sequence
  output      Output MP4 file

optional arguments:
  -h, --help  show this help message and exit

```

# gopro-cut.py

Extract a section of a movie to a separate file, including metadata.

### Usage

```text
usage: gopro-cut.py [-h] [--start START] [--end END] [--duration DURATION] input output

Extract section of GoPro Files

positional arguments:
  input                A single MP4 file
  output               Output MP4 file

optional arguments:
  -h, --help           show this help message and exit
  --start START        Time to start (hh:mm:ss.SSSSSS)
  --end END            Time to end (hh:mm:ss.SSSSSS)
  --duration DURATION  Duration of clip (hh:mm:ss.SSSSSS)
```



# Contributed Programs


# gopro-contrib-data-extract.py

Extract GoPro metadata to an NDJSON file.

### Usage

```
usage: gopro-contrib-data-extract.py [-h] [--fourcc FOURCC] input output

Extract GoPro metadata - Contributed by https://github.com/gregbaker

positional arguments:
  input                 Input file
  output                Output NDJSON file

optional arguments:
  -h, --help            show this help message and exit
  --fourcc FOURCC, -f FOURCC
                        GPMD fourcc field to extract
```
