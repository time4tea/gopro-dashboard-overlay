

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

- Right now, clone the repo, install the dependencies, and run
- Fairly manual process right now...

```bash
git clone https://github.com/time4tea/gopro-dashboard-overlay.git
cd gopro-dashboard-overlay
make venv req
venv/bin/python bin/gopro-dashboard.py ...
```

## Converting to GPX files

```bash
gopro-to-gpx.py <input-file> [output-file]
```

## Overlaying a dashboard

The GPS track in Hero 9 (at least) seems to be very poor. If you supply a GPX file from a Garmin or whatever, the 
program will use this instead for the GPS.

Privacy allows you to set a privacy zone. Various widgets will not draw points within that zone.

```
usage: gopro-dashboard.py [-h] [--gpx GPX] [--privacy PRIVACY] [--no-overlay] input output

Overlay gadgets on to GoPro MP4

positional arguments:
  input              Input MP4 file
  output             Output MP4 file

optional arguments:
  -h, --help         show this help message and exit
  --gpx GPX          Use GPX file for location / alt / hr / cadence / temp
  --privacy PRIVACY  Set privacy zone (lat,lon,km)
  --no-overlay       Only output the gadgets, don't overlay
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


## References

https://github.com/juanmcasillas/gopro2gpx

https://github.com/JuanIrache/gopro-telemetry

https://github.com/gopro/gpmf-parser

