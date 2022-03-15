
### gopro-dashboard.py

## Omitting Widgets

If the layout you are using has a widget you don't want, you can use `--include <name> <name>.. ` or `--exclude <name> <name>...`
on the command line to include or exclude that widget.  To get the name of the widget, currently you need to look at the xml file. (linked above)

## Skipping Containers

If you didn't want to render a container, you could add `--exclude <container-name>` when running the program, and this
container would be skipped.


```
usage: gopro-to-gpx.py [-h] input [output]

Convert GoPro MP4 file to GPX

positional arguments:
  input       Input MP4 file
  output      Output GPX file (default stdout)

optional arguments:
  -h, --help  show this help message and exit
PYTHONPATH=. venv/bin/python bin/gopro-dashboard.py --help
usage: gopro-dashboard.py [-h] [--font FONT] [--gpx GPX] [--privacy PRIVACY] [--overlay-only]
                          [--map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas}]
                          [--map-api-key MAP_API_KEY] [--layout {default,speed-awareness,xml}]
                          [--layout-xml LAYOUT_XML] [--exclude EXCLUDE [EXCLUDE ...]]
                          [--include INCLUDE [INCLUDE ...]] [--show-ffmpeg] [--debug-metadata]
                          [--overlay-size OVERLAY_SIZE] [--output-size OUTPUT_SIZE] [--profile PROFILE]
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
  --overlay-only        Only output the overlay, don't mix with video (default: False)
  --map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas}
                        Style of map to render (default: osm)
  --map-api-key MAP_API_KEY
                        API Key for map provider, if required (default OSM doesn't need one) (default: None)
  --layout {default,speed-awareness,xml}
                        Choose graphics layout (default: default)
  --layout-xml LAYOUT_XML
                        Use XML File for layout [experimental! - file format likely to change!] (default: None)
  --exclude EXCLUDE [EXCLUDE ...]
                        exclude named component (will include all others (default: None)
  --include INCLUDE [INCLUDE ...]
                        include named component (will exclude all others) (default: None)
  --show-ffmpeg         Show FFMPEG output (not usually useful) (default: False)
  --debug-metadata      Show detailed information when parsing GoPro Metadata (default: False)
  --overlay-size OVERLAY_SIZE
                        <XxY> e.g. 1920x1080 Force size of overlay. Use if video differs from supported bundled overlay sizes (1920x1080, 3840x2160) (default: None)
  --output-size OUTPUT_SIZE
                        Vertical size of output movie (default: 1080)
  --profile PROFILE     (EXPERIMENTAL) Use ffmpeg options profile <name> from ~/gopro-graphics/ffmpeg-profiles.json (default: None)
```


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


## gopro-to-gpx.py

```text
usage: gopro-to-gpx.py [-h] input [output]

Convert GoPro MP4 file to GPX

positional arguments:
  input       Input MP4 file
  output      Output GPX file (default stdout)

optional arguments:
  -h, --help  show this help message and exit
```

```text
usage: gopro-join.py [-h] input output

Concatenate sequence of GoPro Files

positional arguments:
  input       A single MP4 file from the sequence
  output      Output MP4 file

optional arguments:
  -h, --help  show this help message and exit

```

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



