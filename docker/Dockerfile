# python:3.11.3-alpine
FROM python@sha256:caafba876f841774905f73df0fcaf7fe3f55aaf9cb48a9e369a41077f860d4a7

MAINTAINER gopro-overlay@time4tea.net
ENV PATH=$PATH:/usr/bin

RUN apk update && apk add bash curl unzip font-noto cairo-dev gcc python3-dev libc-dev ffmpeg sudo
RUN curl "https://fonts.google.com/download?family=Roboto" -o /tmp/Roboto.zip && \
    mkdir -p /usr/share/fonts/Roboto && unzip -d /usr/share/fonts/Roboto /tmp/Roboto.zip && fc-cache -fv

WORKDIR /
RUN python3.11 -mvenv venv
RUN /venv/bin/python3.11 -m pip install --upgrade pip
RUN /venv/bin/pip install pycairo==1.23.0


ARG GOPRO_OVERLAY_VERSION
RUN /venv/bin/pip install gopro-overlay==${GOPRO_OVERLAY_VERSION}

VOLUME /work
WORKDIR /work

COPY entrypoint.sh /

ENTRYPOINT [ "/entrypoint.sh" ]

