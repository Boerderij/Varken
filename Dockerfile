FROM python:3.9.1-alpine

LABEL maintainer="dirtycajunrice,samwiseg0" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/Boerderij/Varken" \
  org.opencontainers.image.source="https://github.com/Boerderij/Varken" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$VCS_REF \
  org.opencontainers.image.vendor="boerderij" \
  org.opencontainers.image.title="varken" \
  org.opencontainers.image.description="Varken is a standalone application to aggregate data from the Plex ecosystem into InfluxDB using Grafana for a frontend" \
  org.opencontainers.image.licenses="MIT"

ENV DEBUG="True"

ENV DATA_FOLDER="/config"

WORKDIR /app

COPY /requirements.txt /Varken.py /app/

COPY /varken /app/varken

COPY /data /app/data

COPY /utilities /app/data/utilities

RUN apk add --no-cache tzdata && \
    pip install --no-cache-dir -r /app/requirements.txt

CMD cp /app/data/varken.example.ini /config/varken.example.ini && python3 /app/Varken.py
