from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta

from varken.structures import Queue, SonarrTVShow
from varken.helpers import hashit, connection_handler


class SonarrAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'X-Api-Key': self.server.api_key}
        self.session.params = {'pageSize': 1000}
        self.logger = getLogger()

    def __repr__(self):
        return f"<sonarr-{self.server.id}>"

    def get_missing(self):
        endpoint = '/api/calendar'
        today = str(date.today())
        last_days = str(date.today() + timedelta(days=-self.server.missing_days))
        now = datetime.now(timezone.utc).astimezone().isoformat()
        params = {'start': last_days, 'end': today}
        influx_payload = []
        missing = []

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        # Iteratively create a list of SonarrTVShow Objects from response json
        tv_shows = []
        for show in get:
            try:
                show_tuple = SonarrTVShow(**show)
                tv_shows.append(show_tuple)
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating SonarrTVShow structure for show', e)
        if not tv_shows:
            return

        # Add show to missing list if file does not exist
        for show in tv_shows:
            if not show.hasFile:
                sxe = f'S{show.seasonNumber:0>2}E{show.episodeNumber:0>2}'
                missing.append((show.series['title'], sxe, show.airDateUtc, show.title, show.id))

        for series_title, sxe, air_date_utc, episode_title, sonarr_id in missing:
            hash_id = hashit(f'{self.server.id}{series_title}{sxe}')
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
                        "airsUTC": air_date_utc
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id

                    }
                }
            )

        self.dbmanager.write_points(influx_payload)

    def get_future(self):
        endpoint = '/api/calendar/'
        today = str(date.today())
        now = datetime.now(timezone.utc).astimezone().isoformat()
        future = str(date.today() + timedelta(days=self.server.future_days))
        influx_payload = []
        air_days = []
        params = {'start': today, 'end': future}

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        tv_shows = []
        for show in get:
            try:
                show_tuple = SonarrTVShow(**show)
                tv_shows.append(show_tuple)
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating SonarrTVShow structure for show', e)
        if not tv_shows:
            return

        for show in tv_shows:
            sxe = f'S{show.seasonNumber:0>2}E{show.episodeNumber:0>2}'
            if show.hasFile:
                downloaded = 1
            else:
                downloaded = 0
            air_days.append((show.series['title'], downloaded, sxe, show.title, show.airDateUtc, show.id))

        for series_title, dl_status, sxe, episode_title, air_date_utc, sonarr_id in air_days:
            hash_id = hashit(f'{self.server.id}{series_title}{sxe}')
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
                        "airsUTC": air_date_utc,
                        "downloaded": dl_status
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        self.dbmanager.write_points(influx_payload)

    def get_queue(self):
        influx_payload = []
        endpoint = '/api/queue'
        now = datetime.now(timezone.utc).astimezone().isoformat()
        queue = []

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        download_queue = []
        for show in get:
            try:
                show_tuple = Queue(**show)
                download_queue.append(show_tuple)
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating Queue structure', e)
        if not download_queue:
            return

        for show in download_queue:
            try:
                sxe = f"S{show.episode['seasonNumber']:0>2}E{show.episode['episodeNumber']:0>2}"
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while processing the sonarr queue. \
                                  Remove invalid queue entries.', e)
                continue

            if show.protocol.upper() == 'USENET':
                protocol_id = 1
            else:
                protocol_id = 0

            queue.append((show.series['title'], show.episode['title'], show.protocol.upper(),
                          protocol_id, sxe, show.id, show.quality['quality']['name']))

        for series_title, episode_title, protocol, protocol_id, sxe, sonarr_id, quality in queue:
            hash_id = hashit(f'{self.server.id}{series_title}{sxe}')
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
                        "protocol_id": protocol_id,
                        "quality": quality
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )
        self.dbmanager.write_points(influx_payload)
