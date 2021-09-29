

# Overlaying Dashboard onto GoPro MP4 Files

- Overlaying exciting graphics
- Converting to GPX files

## Examples

![Example Dashboard Image](examples/2021-09-22-example.png)

## Requirements

- Python3.8
- ffmpeg
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
usage: gopro-dashboard.py [-h] [--gpx GPX] [--privacy PRIVACY] [--no-overlay]
                          [--map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas}]
                          [--map-api-key MAP_API_KEY]
                          input output

Overlay gadgets on to GoPro MP4

positional arguments:
  input                 Input MP4 file
  output                Output MP4 file

optional arguments:
  -h, --help            show this help message and exit
  --gpx GPX             Use GPX file for location / alt / hr / cadence / temp
  --privacy PRIVACY     Set privacy zone (lat,lon,km)
  --no-overlay          Only output the gadgets, don't overlay
  --map-style {osm,tf-cycle,tf-transport,tf-landscape,tf-outdoors,tf-transport-dark,tf-spinal-map,tf-pioneer,tf-mobile-atlas,tf-neighbourhood,tf-atlas}
                        Style of map to render
  --map-api-key MAP_API_KEY
                        API Key for map provider, if required (default OSM doesn't need one)
```

## Example

```shell
venv/bin/gopro-dashboard.py --gpx ~/Downloads/Morning_Ride.gpx --privacy 52.000,-0.40000,0.50 ~/gopro/GH020073.MP4 GH020073-dashboard.MP4
```


## Performance

No attempt has been made to optimise this program! Right now, on my machine, it renders an 11 minute file in about 7 mins.

## Known Bugs / Issues

- Aligning overlay with video - not exact! - Start garmin first, and wait for GPS lock before recording
- Multiple GoPro files concatentated and overlayed. Current limit of 10 mins (in 1080p/60) is annoying.

## Controlling the dashbord layout / controlling widgets

Its all hard coded right now.

## Icons

Icon files in [icons](gopro_overlay/icons) are not covered by the MIT licence

## Map Data

Data © [OpenStreetMap contributors](http://www.openstreetmap.org/copyright)

Some Maps © [Thunderforest](http://www.thunderforest.com/)

## References

https://github.com/juanmcasillas/gopro2gpx

https://github.com/JuanIrache/gopro-telemetry

https://github.com/gopro/gpmf-parser

