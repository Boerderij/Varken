from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta

from varken.structures import LidarrQueue, LidarrAlbum
from varken.helpers import hashit, connection_handler


class LidarrAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'X-Api-Key': self.server.api_key}
        self.logger = getLogger()

    def __repr__(self):
        return f"<lidarr-{self.server.id}>"

    def get_calendar(self, query="Missing"):
        endpoint = '/api/v1/calendar'
        today = str(date.today())
        last_days = str(date.today() - timedelta(days=self.server.missing_days))
        future = str(date.today() + timedelta(days=self.server.future_days))
        now = datetime.now(timezone.utc).astimezone().isoformat()
        if query == "Missing":
            params = {'start': last_days, 'end': today}
        else:
            params = {'start': today, 'end': future}
        influx_payload = []
        influx_albums = []

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        # Iteratively create a list of LidarrAlbum Objects from response json
        albums = []
        for album in get:
            try:
                albums.append(LidarrAlbum(**album))
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating LidarrAlbum structure for album. Data '
                                  'attempted is: %s', e, album)

        # Add Album to missing list if album is not complete
        for album in albums:
            percent_of_tracks = album.statistics.get('percentOfTracks', 0)
            if percent_of_tracks != 100:
                influx_albums.append(
                    (album.title, album.releaseDate, album.artist['artistName'], album.id, percent_of_tracks,
                     f"{album.statistics.get('trackFileCount', 0)}/{album.statistics.get('trackCount', 0)}")
                )

        for title, release_date, artist_name, album_id, percent_complete, complete_count in influx_albums:
            hash_id = hashit(f'{self.server.id}{title}{album_id}')
            influx_payload.append(
                {
                    "measurement": "Lidarr",
                    "tags": {
                        "type": query,
                        "sonarrId": album_id,
                        "server": self.server.id,
                        "albumName": title,
                        "artistName": artist_name,
                        "percentComplete": percent_complete,
                        "completeCount": complete_count,
                        "releaseDate": release_date
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id

                    }
                }
            )

        self.dbmanager.write_points(influx_payload)

    def get_queue(self):
        endpoint = '/api/v1/queue'
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        params = {'pageSize': 1000}

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        queue = []
        for song in get['records']:
            try:
                queue.append(LidarrQueue(**song))
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating LidarrQueue structure for show. Data '
                                  'attempted is: %s', e, song)

        if not queue:
            return

        for song in queue:
            if song.protocol.upper() == 'USENET':
                protocol_id = 1
            else:
                protocol_id = 0
            hash_id = hashit(f'{self.server.id}{song.title}{song.artistId}')
            influx_payload.append(
                {
                    "measurement": "Lidarr",
                    "tags": {
                        "type": "Queue",
                        "id": song.id,
                        "server": self.server.id,
                        "title": song.title,
                        "quality": song.quality['quality']['name'],
                        "protocol": song.protocol,
                        "protocol_id": protocol_id,
                        "indexer": song.indexer
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        self.dbmanager.write_points(influx_payload)
