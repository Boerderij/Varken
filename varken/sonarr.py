import logging
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta

from varken.helpers import hashit, connection_handler
from varken.structures import Queue, TVShow


class SonarrAPI(object):
    def __init__(self, server, dbmanager):
        # Set Time of initialization
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.dbmanager = dbmanager
        self.today = str(date.today())
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'X-Api-Key': self.server.api_key}
        self.session.params = {'pageSize': 1000}
        self.logger = logging.getLogger()

    def __repr__(self):
        return "<sonarr-{}>".format(self.server.id)

    def get_missing(self):
        endpoint = '/api/calendar'
        last_days = str(date.today() + timedelta(days=-self.server.missing_days))
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        params = {'start': last_days, 'end': self.today}
        influx_payload = []
        missing = []

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        # Iteratively create a list of TVShow Objects from response json
        try:
            tv_shows = [TVShow(**show) for show in get]
        except TypeError as e:
            self.logger.error('TypeError has occurred : %s while creating TVShow structure', e)
            return

        # Add show to missing list if file does not exist
        for show in tv_shows:
            if not show.hasFile:
                sxe = 'S{:0>2}E{:0>2}'.format(show.seasonNumber, show.episodeNumber)
                missing.append((show.series['title'], sxe, show.airDate, show.title, show.id))

        for series_title, sxe, air_date, episode_title, sonarr_id in missing:
            hash_id = hashit('{}{}{}'.format(self.server.id, series_title, sxe))
            influx_payload.append(
                {
                    "measurement": "Sonarr",
                    "tags": {
                        "type": "Missing",
                        "sonarrId": sonarr_id,
                        "server": self.server.id,
                        "name": series_title,
                        "epname": episode_title,
                        "sxe": sxe,
                        "airs": air_date
                    },
                    "time": self.now,
                    "fields": {
                        "hash": hash_id

                    }
                }
            )

        self.dbmanager.write_points(influx_payload)

    def get_future(self):
        endpoint = '/api/calendar/'
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        future = str(date.today() + timedelta(days=self.server.future_days))
        influx_payload = []
        air_days = []
        params = {'start': self.today, 'end': future}

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        try:
            tv_shows = [TVShow(**show) for show in get]
        except TypeError as e:
            self.logger.error('TypeError has occurred : %s while creating TVShow structure', e)
            return

        for show in tv_shows:
            sxe = 'S{:0>2}E{:0>2}'.format(show.seasonNumber, show.episodeNumber)
            if show.hasFile:
                downloaded = 1
            else:
                downloaded = 0
            air_days.append((show.series['title'], downloaded, sxe, show.title, show.airDate, show.id))

        for series_title, dl_status, sxe, episode_title, air_date, sonarr_id in air_days:
            hash_id = hashit('{}{}{}'.format(self.server.id, series_title, sxe))
            influx_payload.append(
                {
                    "measurement": "Sonarr",
                    "tags": {
                        "type": "Future",
                        "sonarrId": sonarr_id,
                        "server": self.server.id,
                        "name": series_title,
                        "epname": episode_title,
                        "sxe": sxe,
                        "airs": air_date,
                        "downloaded": dl_status
                    },
                    "time": self.now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        self.dbmanager.write_points(influx_payload)

    def get_queue(self):
        influx_payload = []
        endpoint = '/api/queue'
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        queue = []

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        try:
            download_queue = [Queue(**show) for show in get]
        except TypeError as e:
            self.logger.error('TypeError has occurred : %s while creating Queue structure', e)
            return

        for show in download_queue:
            sxe = 'S{:0>2}E{:0>2}'.format(show.episode['seasonNumber'], show.episode['episodeNumber'])
            if show.protocol.upper() == 'USENET':
                protocol_id = 1
            else:
                protocol_id = 0

            queue.append((show.series['title'], show.episode['title'], show.protocol.upper(),
                          protocol_id, sxe, show.id))

        for series_title, episode_title, protocol, protocol_id, sxe, sonarr_id in queue:
            hash_id = hashit('{}{}{}'.format(self.server.id, series_title, sxe))
            influx_payload.append(
                {
                    "measurement": "Sonarr",
                    "tags": {
                        "type": "Queue",
                        "sonarrId": sonarr_id,
                        "server": self.server.id,
                        "name": series_title,
                        "epname": episode_title,
                        "sxe": sxe,
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
