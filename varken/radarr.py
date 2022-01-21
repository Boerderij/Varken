from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.structures import QueuePages, RadarrMovie, RadarrQueue
from varken.helpers import hashit, connection_handler


class RadarrAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'X-Api-Key': self.server.api_key}
        self.logger = getLogger()

    def __repr__(self):
        return f"<radarr-{self.server.id}>"

    def get_missing(self):
        endpoint = '/api/v3/movie'
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        missing = []

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        try:
            movies = [RadarrMovie(**movie) for movie in get]
        except TypeError as e:
            self.logger.error('TypeError has occurred : %s while creating RadarrMovie structure', e)
            return

        for movie in movies:
            if movie.monitored and not movie.hasFile:
                if movie.isAvailable:
                    ma = 0
                else:
                    ma = 1

                movie_name = f'{movie.title} ({movie.year})'
                missing.append((movie_name, ma, movie.tmdbId, movie.titleSlug))

        for title, ma, mid, title_slug in missing:
            hash_id = hashit(f'{self.server.id}{title}{mid}')
            influx_payload.append(
                {
                    "measurement": "Radarr",
                    "tags": {
                        "Missing": True,
                        "Missing_Available": ma,
                        "tmdbId": mid,
                        "server": self.server.id,
                        "name": title,
                        "titleSlug": title_slug
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        if influx_payload:
            self.dbmanager.write_points(influx_payload)
        else:
            self.logger.warning("No data to send to influx for radarr-missing instance, discarding.")

    def get_queue(self):
        endpoint = '/api/v3/queue'
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        pageSize = 250
        params = {'pageSize': pageSize, 'includeMovie': True, 'includeUnknownMovieItems': False}
        queueResponse = []
        queue = []

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        response = QueuePages(**get)
        queueResponse.extend(response.records)

        while response.totalRecords > response.page * response.pageSize:
            page = response.page + 1
            params = {'pageSize': pageSize, 'page': page, 'includeMovie': True, 'includeUnknownMovieItems': False}
            req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
            get = connection_handler(self.session, req, self.server.verify_ssl)
            if not get:
                return

            response = QueuePages(**get)
            queueResponse.extend(response.records)

        download_queue = []
        for queueItem in queueResponse:
            try:
                download_queue.append(RadarrQueue(**queueItem))
            except TypeError as e:
                self.logger.warning('TypeError has occurred : %s while creating RadarrQueue structure', e)
                return
        if not download_queue:
            self.logger.warning("No data to send to influx for radarr-queue instance, discarding.")
            return

        for queue_item in download_queue:
            movie = RadarrMovie(**queue_item.movie)

            name = f'{movie.title} ({movie.year})'

            if queue_item.protocol.upper() == 'USENET':
                protocol_id = 1
            else:
                protocol_id = 0

            queue.append((name, queue_item.quality['quality']['name'], queue_item.protocol.upper(),
                          protocol_id, queue_item.id, movie.titleSlug))

        for name, quality, protocol, protocol_id, qid, title_slug in queue:
            hash_id = hashit(f'{self.server.id}{name}{quality}')
            influx_payload.append(
                {
                    "measurement": "Radarr",
                    "tags": {
                        "type": "Queue",
                        "tmdbId": qid,
                        "server": self.server.id,
                        "name": name,
                        "quality": quality,
                        "protocol": protocol,
                        "protocol_id": protocol_id,
                        "titleSlug": title_slug
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        if influx_payload:
            self.dbmanager.write_points(influx_payload)
        else:
            self.logger.warning("No data to send to influx for radarr-queue instance, discarding.")
