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

*Create a movie, using GPU encoding and decoding*

You'll need to create a profile - see [FFMPEG Profiles](#ffmpeg-profiles)

```shell
venv/bin/gopro-dashboard.py --profile nvgpu ~/layouts/my-layout.xml ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
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

### Usage

```
usage: gopro-dashboard.py [-h] [--font FONT] [--gpx GPX] [--privacy PRIVACY]
                          [--map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas,geo-osm-carto,geo-osm-bright,geo-osm-bright-grey,geo-osm-bright-smooth,geo-klokantech-basic,geo-osm-liberty,geo-maptiler-3d,geo-toner,geo-toner-grey,geo-positron,geo-positron-blue,geo-positron-red,geo-dark-matter,geo-dark-matter-brown,geo-dark-matter-dark-grey,geo-dark-matter-dark-purple,geo-dark-matter-purple-roads,geo-dark-matter-yellow-roads}]
                          [--map-api-key MAP_API_KEY] [--layout {default,speed-awareness,xml}]
                          [--layout-xml LAYOUT_XML] [--exclude EXCLUDE [EXCLUDE ...]]
                          [--include INCLUDE [INCLUDE ...]] [--generate {default,overlay,none}]
                          [--show-ffmpeg] [--debug-metadata] [--overlay-size OVERLAY_SIZE]
                          [--output-size OUTPUT_SIZE] [--profile PROFILE] [--thread]
                          input output

Overlay gadgets on to GoPro MP4

positional arguments:
  input                 Input MP4 file
  output                Output MP4 file

optional arguments:
  -h, --help            show this help message and exit
  --font FONT           Selects a font (default: Roboto-Medium.ttf)
  --gpx GPX             Use GPX file for location / alt / hr / cadence / temp (default: None)
  --privacy PRIVACY     Set privacy zone (lat,lon,km) (default: None)
  --map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas,geo-osm-carto,geo-osm-bright,geo-osm-bright-grey,geo-osm-bright-smooth,geo-klokantech-basic,geo-osm-liberty,geo-maptiler-3d,geo-toner,geo-toner-grey,geo-positron,geo-positron-blue,geo-positron-red,geo-dark-matter,geo-dark-matter-brown,geo-dark-matter-dark-grey,geo-dark-matter-dark-purple,geo-dark-matter-purple-roads,geo-dark-matter-yellow-roads}
                        Style of map to render (default: osm)
  --map-api-key MAP_API_KEY
                        API Key for map provider, if required (default OSM doesn't need one) (default: None)
  --layout {default,speed-awareness,xml}
                        Choose graphics layout (default: default)
  --layout-xml LAYOUT_XML
                        Use XML File for layout [experimental! - file format likely to change!] (default:
                        None)
  --exclude EXCLUDE [EXCLUDE ...]
                        exclude named component (will include all others (default: None)
  --include INCLUDE [INCLUDE ...]
                        include named component (will exclude all others) (default: None)
  --generate {default,overlay,none}
                        Type of output to generate (default: default)
  --show-ffmpeg         Show FFMPEG output (not usually useful) (default: False)
  --debug-metadata      Show detailed information when parsing GoPro Metadata (default: False)
  --overlay-size OVERLAY_SIZE
                        <XxY> e.g. 1920x1080 Force size of overlay. Use if video differs from supported
                        bundled overlay sizes (1920x1080, 3840x2160) (default: None)
  --output-size OUTPUT_SIZE
                        Vertical size of output movie (default: 1080)
  --profile PROFILE     (EXPERIMENTAL) Use ffmpeg options profile <name> from ~/gopro-graphics/ffmpeg-
                        profiles.json (default: None)
  --thread              (VERY EXPERIMENTAL MAY CRASH) Use an intermediate buffer before ffmpeg as possible
                        performance enhancement (default: False)
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
usage: gopro-rename.py [-h] [--desc DESC] [--geo] [--yes] [--dirs] file [file ...]

Rename a series of GoPro files by date. Does nothing (so its safe) by default.

positional arguments:
  file         The files to rename, or directory/ies containing files

optional arguments:
  -h, --help   show this help message and exit
  --desc DESC  a descriptive name to add to the filename - the filename will be yyyymmdd-hhmmss-{desc}.MP4
  --geo        [EXPERIMENTAL] Use Geocode.xyz to add description for you (city-state) - see
               https://geocode.xyz/pricing for terms
  --yes        Rename the files, don't just print what would be done
  --dirs       Allow directory
```

# gopro-to-csv.py

Convert GoPro metadata to a CSV file.

Not hugely flexible at the moment.

### Usage

```text
usage: gopro-to-csv.py [-h] [--gpx] input [output]

Convert GoPro MP4 file / GPX File to CSV

positional arguments:
  input       Input file
  output      Output CSV file (default stdout)

optional arguments:
  -h, --help  show this help message and exit
  --gpx       Input is a gpx file
```

# gopro-to-gpx.py

Convert GoPro metadata to a GPX file for upload/import into other software

### Usage

```text
usage: gopro-to-gpx.py [-h] input [output]

Convert GoPro MP4 file to GPX

positional arguments:
  input       Input MP4 file
  output      Output GPX file (default stdout)

optional arguments:
  -h, --help  show this help message and exit
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
