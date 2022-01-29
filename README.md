

# Overlaying Dashboard onto GoPro MP4 Files

- Overlaying exciting graphics
- Converting to GPX files

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

## Converting to GPX files

```shell
venv/bin/gopro-to-gpx.py <input-file> [output-file]
```

## Overlaying a dashboard

```shell
venv/bin/gopro-dashboard.py
```


The GPS track in Hero 9 (at least) seems to be very poor. If you supply a GPX file from a Garmin or whatever, the 
program will use this instead for the GPS.

Privacy allows you to set a privacy zone. Various widgets will not draw points within that zone.

```
usage: gopro-dashboard.py [-h] [--font FONT] [--gpx GPX] [--privacy PRIVACY] [--no-overlay]
                          [--map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas}]
                          [--map-api-key MAP_API_KEY] [--layout {default,speed-awareness,xml}] [--layout-xml LAYOUT_XML] [--show-ffmpeg]
                          [--output-size OUTPUT_SIZE]
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
  --no-overlay          Only output the gadgets, don't overlay (default: True)
  --map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas}
                        Style of map to render (default: osm)
  --map-api-key MAP_API_KEY
                        API Key for map provider, if required (default OSM doesn't need one) (default: None)
  --layout {default,speed-awareness,xml}
                        Choose graphics layout (default: default)
  --layout-xml LAYOUT_XML
                        Use XML File for layout [experimental! - file format likely to change!] (default: None)
  --show-ffmpeg         Show FFMPEG output (not usually useful) (default: False)
  --output-size OUTPUT_SIZE
                        Vertical size of output movie (default: 1080)

```

## Example

```shell
venv/bin/gopro-dashboard.py --gpx ~/Downloads/Morning_Ride.gpx --privacy 52.000,-0.40000,0.50 ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```


## Performance

No attempt has been made to optimise this program! Right now, on my machine, it renders an 11 minute file in about 7 mins.

## Known Bugs / Issues

- Only tested on a GoPro Hero 9, that's all I have. Sample files for other devices are welcomed.
- Aligning overlay with video - not exact! - Start garmin first, and wait for GPS lock before recording
- Multiple GoPro files concatentated and overlayed. Current limit of 10 mins (in 1080p/60) is annoying.

## Controlling the dashboard layout / controlling widgets

Primitive XML Configuration file support - By using the parameters `--layout xml --layout-xml <filename>` you can get
configure the layout yourself. Its very basic right now, but allows you to choose which elements you want.

Have a look at the [example file](gopro_overlay/layouts/example.xml) to see an example. 

## Icons

Icon files in [icons](gopro_overlay/icons) are not covered by the MIT licence

## Map Data

Data © [OpenStreetMap contributors](http://www.openstreetmap.org/copyright)

Some Maps © [Thunderforest](http://www.thunderforest.com/)

## References

https://github.com/juanmcasillas/gopro2gpx

https://github.com/JuanIrache/gopro-telemetry

https://github.com/gopro/gpmf-parser

## Other Related Software

https://github.com/progweb/gpx2video

https://github.com/JuanIrache/gopro-telemetry


## Latest Changes

- Unreleased
  - Improve Parsing Speed for GoPro
- 0.11.0 
  - Allow XML layout definitions 
  