from requests import Session
from datetime import datetime, timezone

from Varken.logger import logging
from Varken.helpers import Movie, Queue, hashit


class RadarrAPI(object):
    def __init__(self, server, dbmanager):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'X-Api-Key': self.server.api_key}

    @logging
    def get_missing(self):
        endpoint = '/api/movie'
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        missing = []

        get = self.session.get(self.server.url + endpoint, verify=self.server.verify_ssl).json()
        movies = [Movie(**movie) for movie in get]

        for movie in movies:
            if self.server.get_missing:
                if not movie.downloaded and movie.isAvailable:
                    ma = True
                else:
                    ma = False
                movie_name = '{} ({})'.format(movie.title, movie.year)
                missing.append((movie_name, ma, movie.tmdbId))

        for title, ma, mid in missing:
            hash_id = hashit('{}{}{}'.format(self.server.id, title, mid))
            influx_payload.append(
                {
                    "measurement": "Radarr",
                    "tags": {
                        "Missing": True,
                        "Missing_Available": ma,
                        "tmdbId": mid,
                        "server": self.server.id,
                        "name": title
                    },
                    "time": self.now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        self.dbmanager.write_points(influx_payload)

    @logging
    def get_queue(self):
        endpoint = '/api/queue'
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        queue = []
        get = self.session.get(self.server.url + endpoint, verify=self.server.verify_ssl).json()
        for movie in get:
            movie['movie'] = Movie(**movie['movie'])
        download_queue = [Queue(**movie) for movie in get]

        for queue_item in download_queue:
            name = '{} ({})'.format(queue_item.movie.title, queue_item.movie.year)

            if queue_item.protocol.upper() == 'USENET':
                protocol_id = 1
            else:
                protocol_id = 0

            queue.append((name, queue_item.quality['quality']['name'], queue_item.protocol.upper(),
                          protocol_id, queue_item.id))

        for movie, quality, protocol, protocol_id, qid in queue:
            hash_id = hashit('{}{}{}'.format(self.server.id, movie, quality))
            influx_payload.append(
                {
                    "measurement": "Radarr",
                    "tags": {
                        "type": "Queue",
                        "tmdbId": qid,
                        "server": self.server.id,
                        "name": movie,
                        "quality": quality,
                        "protocol": protocol,
                        "protocol_id": protocol_id
                    },
                    "time": self.now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        self.dbmanager.write_points(influx_payload)
