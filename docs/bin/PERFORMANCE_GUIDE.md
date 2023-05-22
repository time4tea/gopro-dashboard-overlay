# How to get best performance

Rendering graphics & video is computationally intensive, and python is not known for being fast.

Here we'll talk about how to get the best performance out of `gopro-dashboard` - it does require 

### What levels of performance are achievable?

On a 2016-era CPU and an NVIDIA 3060 graphics card, 110 overlay frames/second, which corresponds to about 17x realtime.
In other words, a 20 min gopro video can render in about 1.5 mins, at 1920x1080.

In this guide, we'll look at some different configurations, all running on this computer.

When creating an overlay video, we write 10 dashboard frames every second, so 10fps here means we can generate 
1 second of video each second of real time. In other words 10fps = 1x realtime

This guide was written using version 0.93.0 of gopro-dashboard. "ffmpeg profiles" are a feature of gopro-dashboard - please see the docs about how to create them.

### What affects performance?

- Version of Python
- Version of ffmpeg
- Use of Pillow-SIMD
- Dimensions of video frame
- Use of double-buffering mode
- GPU & Using it for as much as possible
- Overlay widgets & complexity


### Baseline - python3.10, ffmpeg 4.4.2

This is the default for Ubuntu 22.04.

`venv/bin/gopro-dashboard.py GOPR0186.MP4 GOPR0186-overlay.MP4`

```none
Starting gopro-dashboard version 0.92.0
ffmpeg version is 4.4.2-0ubuntu0.22.04.1
Using Python version 3.10.6 (main, Mar 10 2023, 10:55:28) [GCC 11.3.0]
    Timer(GPMD - Called: 1, Total: 0.09643, Avg: 0.09643, Rate: 10.37)
    Timer(extract GPS - Called: 1, Total: 1.67421, Avg: 1.67421, Rate: 0.60)
Generating overlay at Dimension(x=1920, y=1080)
Timer(drawing frames - Called: 500, Total: 32.15302, Avg: 0.06431, Rate: 15.55)
```

Baseline: approx 16fps = 1.6x realtime


### Upgrade ffmpeg - Python3.10, ffmpeg 6.0

`venv/bin/gopro-dashboard.py GOPR0186.MP4 GOPR0186-overlay.MP4`

```none
Starting gopro-dashboard version 0.92.0
ffmpeg version is 6.0
Using Python version 3.10.6 (main, Mar 10 2023, 10:55:28) [GCC 11.3.0]
    Timer(GPMD - Called: 1, Total: 0.10205, Avg: 0.10205, Rate: 9.80)
    Timer(extract GPS - Called: 1, Total: 1.67341, Avg: 1.67341, Rate: 0.60)
Generating overlay at Dimension(x=1920, y=1080)
Timer(drawing frames - Called: 511, Total: 25.24729, Avg: 0.04941, Rate: 20.24)
```

Upgrade ffmpeg: 20fps = 2x realtime

### Python 3.11, ffmpeg 6.0

`venv/bin/gopro-dashboard.py GOPR0186.MP4 GOPR0186-overlay.MP4`

```
Starting gopro-dashboard version 0.92.0
ffmpeg version is 6.0
Using Python version 3.11.3 (main, Apr  5 2023, 14:14:37) [GCC 11.3.0]
    Timer(GPMD - Called: 1, Total: 0.06115, Avg: 0.06115, Rate: 16.35)
    Timer(extract GPS - Called: 1, Total: 1.28409, Avg: 1.28409, Rate: 0.78)
Timer(drawing frames - Called: 509, Total: 25.09252, Avg: 0.04930, Rate: 20.28)
```

20fps = 2x realtime

### Python 3.11, ffmpeg 6.0, double-buffer

`venv/bin/gopro-dashboard.py --double-buffer GOPR0186.MP4 GOPR0186-overlay.MP4`

```
Starting gopro-dashboard version 0.92.0
ffmpeg version is 6.0
Using Python version 3.11.3 (main, Apr  5 2023, 14:14:37) [GCC 11.3.0]
*** NOTE: Double Buffer mode is experimental. It is believed to work fine on Linux. Please raise issues if you see it working or not-working. Thanks ***
Timer(drawing frames - Called: 507, Total: 22.28614, Avg: 0.04396, Rate: 22.75)
```

22.75fps


### Python 3.11, ffmpeg 6.0, double-buffer, Pillow-SIMD

Update to pillow-simd

```
venv/bin/pip uninstall pillow
venv/bin/pip install pillow-simd==8.3.2.post0
```

generate dashboard 

`venv/bin/gopro-dashboard.py --double-buffer GOPR0186.MP4 GOPR0186-overlay.MP4`

```text
Timer(drawing frames - Called: 507, Total: 20.22795, Avg: 0.03990, Rate: 25.06)
```

25fps

### Python 3.11, ffmpeg 6.0, double-buffer, Pillow-SIMD, partial GPU

This setting will also work on ffmpeg 4.4, if you cannot upgrade to later version.

Update to pillow-simd

```
venv/bin/pip uninstall pillow
venv/bin/pip install pillow-simd==8.3.2.post0
```

Create ffmpeg profile - this uses "nvdec" to decode gopro mpeg, "nvenc" to encode it.

```json
{
  "nvgpu": {
    "input": ["-hwaccel", "nvdec"],
    "output": ["-vcodec", "h264_nvenc", "-rc:v", "cbr", "-b:v", "40M", "-bf:v", "3", "-profile:v", "high", "-spatial-aq", "true", "-movflags", "faststart"]
  }
}
```

generate dashboard

`venv/bin/gopro-dashboard.py --profile nvgpu --double-buffer GOPR0186.MP4 GOPR0186-overlay.MP4`

```text
Timer(drawing frames - Called: 495, Total: 9.05593, Avg: 0.01829, Rate: 54.66)
```

54.66fps


### Python 3.11, ffmpeg 6.0, double-buffer, Pillow-SIMD, Full GPU

This setting will only work on newer versions of ffmpeg, 5.x+ - not sure what `x` is.

Update to pillow-simd, as above.

Create ffmpeg profile - this uses CUDA to decode the gopro mpeg, keeps the frame in hardware, does the overlay in hardware, and also encoding in hardware. 

```json
{
    "nnvgpu": {
    "input": ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda" ],
    "filter": "[0:v]scale_cuda=format=yuv420p[mp4_stream];[1:v]format=yuva420p,hwupload[overlay_stream];[mp4_stream][overlay_stream]overlay_cuda",
    "output": ["-vcodec", "h264_nvenc", "-rc:v", "cbr", "-b:v", "40M", "-bf:v", "3", "-profile:v", "main", "-spatial-aq", "true", "-movflags", "faststart"]
  }
}
```

generate dashboard

`venv/bin/gopro-dashboard.py --profile nnvgpu --double-buffer GOPR0186.MP4 GOPR0186-overlay.MP4`

```text
Timer(drawing frames - Called: 614, Total: 5.42664, Avg: 0.00884, Rate: 113.15)
```

__113.5fps = 11x realtime__


