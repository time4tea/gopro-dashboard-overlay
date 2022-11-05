# 3.16.2/linux/amd64
FROM alpine@sha256:1304f174557314a7ed9eddb4eab12fed12cb0cd9809e4c28f29af86979a3c870

ARG GOPRO_OVERLAY_VERSION

MAINTAINER gopro-overlay@time4tea.net
ENV PATH=$PATH:/usr/bin

RUN apk update && apk add bash python3 py3-pip curl unzip font-noto ffmpeg sudo
RUN curl "https://fonts.google.com/download?family=Roboto" -o /tmp/Roboto.zip && \
    mkdir -p /usr/share/fonts/Roboto && unzip -d /usr/share/fonts/Roboto /tmp/Roboto.zip && fc-cache -fv

WORKDIR /
RUN python3 -mvenv venv
RUN /venv/bin/python3 -m pip install --upgrade pip
RUN /venv/bin/pip install gopro-overlay==${GOPRO_OVERLAY_VERSION}

VOLUME /work
WORKDIR /work

COPY entrypoint.sh /

ENTRYPOINT [ "/entrypoint.sh" ]

