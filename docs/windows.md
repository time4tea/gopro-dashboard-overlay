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

