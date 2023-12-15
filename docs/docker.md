## Installing and running with docker

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

## Using a GPU with docker

I only know how to run NVIDIA GPUs - Instructions for other manufacturers are welcomed!

First, you need to make sure that the **host** environment is configured correctly. 

### Installing NVIDIA Container Toolkit

https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

### Running the container with GPU access

Pass in the `--gpus all` flag to docker...

Set up a profile, say in `config` directory. (See profiles documentation) - that uses the GPU.

```shell
docker run --gpus all -it -v "$(pwd):/work" overlaydash/gopro-dashboard-overlay gopro-dashboard.py --config-dir=config --double-buffer --profile=nnvgpu input-file.mp4 output-file.mp4
```

