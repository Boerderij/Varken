FROM python:3.10.5-alpine

ENV DEBUG="True" \
    DATA_FOLDER="/config" \
    VERSION="0.0.0" \
    BRANCH="edge" \
    BUILD_DATE="1/1/1970"

LABEL maintainer="MDHMatt" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/MDHMatt/Biggetje" \
  org.opencontainers.image.source="https://github.com/MDHMatt/Biggetje" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$VCS_REF \
  org.opencontainers.image.vendor="MDHMatt" \
  org.opencontainers.image.title="Biggetje" \
  org.opencontainers.image.description="Biggetje (Piglet) child of Varken (Pig), is a standalone application to aggregate data from the Plex and the *arrs into InfluxDB using Grafana for a frontend" \
  org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY /requirements.txt /Varken.py /app/

COPY /varken /app/varken

COPY /data /app/data

COPY /utilities /app/data/utilities

RUN \
  apk add --no-cache tzdata \
  && pip install --no-cache-dir -r /app/requirements.txt \
  && sed -i "s/0.0.0/${VERSION}/;s/develop/${BRANCH}/;s/1\/1\/1970/${BUILD_DATE//\//\\/}/" varken/__init__.py

CMD cp /app/data/varken.example.ini /config/varken.example.ini && python3 /app/Varken.py
