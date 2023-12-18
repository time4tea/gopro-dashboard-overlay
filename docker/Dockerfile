FROM ubuntu:23.10

MAINTAINER gopro-overlay@time4tea.net
ENV PATH=$PATH:/usr/bin


RUN apt update && apt install -y curl gnupg unzip fonts-noto fonts-roboto python3.11 ffmpeg sudo libcairo-dev

WORKDIR /
RUN apt install -y python3.11-venv
RUN python3.11 -mvenv venv
RUN /venv/bin/python3.11 -m pip install --upgrade pip

RUN apt install -y gcc
RUN apt install -y python3.11-dev libcairo2-dev pkg-config
RUN /venv/bin/pip install pycairo==1.23.0

RUN apt install -y libnvidia-decode-535-server libnvidia-encode-535-server
ARG GOPRO_OVERLAY_VERSION
RUN /venv/bin/pip install gopro-overlay==${GOPRO_OVERLAY_VERSION}

RUN apt install -y libjpeg-dev
RUN /venv/bin/pip uninstall -y pillow
RUN /venv/bin/pip install pillow-simd==8.3.2.post0

VOLUME /work
WORKDIR /work

COPY entrypoint.sh /

ENTRYPOINT [ "/entrypoint.sh" ]

