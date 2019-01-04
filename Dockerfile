FROM lsiobase/alpine.python3

LABEL maintainer="dirtycajunrice"

ENV DEBUG="False"

COPY / /app

RUN \
    python3 -m pip install -r /app/requirements.txt && \
    chown -R abc:abc \
    /config \
    /app

WORKDIR /app

CMD cp /app/data/varken.example.ini /config/varken.example.ini && python3 /app/Varken.py --data-folder /config

VOLUME /config
