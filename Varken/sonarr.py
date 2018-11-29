#!/usr/bin/env python3
# Do not edit this script. Edit configuration.py
import requests
from influxdb import InfluxDBClient
from datetime import datetime, timezone, date, timedelta

from Varken.logger import logging
from Varken.helpers import TVShow, Queue


class SonarrAPI(object):
    def __init__(self, sonarr_servers, influx_server):
        # Set Time of initialization
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.today = str(date.today())
        self.influx = InfluxDBClient(influx_server.url, influx_server.port, influx_server.username,
                                     influx_server.password, 'plex')
        self.servers = sonarr_servers
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = requests.Session()
        self.session.params = {'pageSize': 1000}

    @logging
    def get_missing(self, days_past):
        endpoint = '/api/calendar'
        last_days = str(date.today() + timedelta(days=-days_past))
        params = {'start': last_days, 'end': self.today}
        influx_payload = []

        for server in self.servers:
            missing = []
            headers = {'X-Api-Key': server.api_key}

            get = self.session.get(server.url + endpoint, params=params, headers=headers,
                                   verify=server.verify_ssl).json()
            # Iteratively create a list of TVShow Objects from response json
            tv_shows = [TVShow(**show) for show in get]

            # Add show to missing list if file does not exist
            for show in tv_shows:
                if not show.hasFile:
                    sxe = 'S{:0>2}E{:0>2}'.format(show.seasonNumber, show.episodeNumber)
                    missing.append((show.series['title'], sxe, show.airDate, show.title, show.id))

            for series_title, sxe, air_date, episode_title, sonarr_id in missing:
                influx_payload.append(
                    {
                        "measurement": "Sonarr",
                        "tags": {
                            "type": "Missing",
                            "sonarrId": sonarr_id,
                            "server": server.id
                        },
                        "time": self.now,
                        "fields": {
                            "name": series_title,
                            "epname": episode_title,
                            "sxe": sxe,
                            "airs": air_date
                        }
                    }
                )

        self.influx_push(influx_payload)

    @logging
    def get_future(self, future_days):
        endpoint = '/api/calendar/'
        future = str(date.today() + timedelta(days=future_days))
        influx_payload = []

        for server in self.servers:
            air_days = []

            headers = {'X-Api-Key': server.api_key}
            params = {'start': self.today, 'end': future}

            get = self.session.get(server.url + endpoint, params=params, headers=headers,
                                   verify=server.verify_ssl).json()
            tv_shows = [TVShow(**show) for show in get]

            for show in tv_shows:
                sxe = 'S{:0>2}E{:0>2}'.format(show.seasonNumber, show.episodeNumber)
                air_days.append((show.series['title'], show.hasFile, sxe, show.title, show.airDate, show.id))

            for series_title, dl_status, sxe, episode_title, air_date, sonarr_id in air_days:
                influx_payload.append(
                    {
                        "measurement": "Sonarr",
                        "tags": {
                            "type": "Future",
                            "sonarrId": sonarr_id,
                            "server": server.id
                        },
                        "time": self.now,
                        "fields": {
                            "name": series_title,
                            "epname": episode_title,
                            "sxe": sxe,
                            "airs": air_date,
                            "downloaded": dl_status
                        }
                    }
                )

        self.influx_push(influx_payload)

    @logging
    def get_queue(self, notimplemented):
        influx_payload = []
        endpoint = '/api/queue'

        for server in self.servers:
            queue = []
            headers = {'X-Api-Key': server.api_key}

            get = self.session.get(server.url + endpoint, headers=headers, verify=server.verify_ssl).json()
            download_queue = [Queue(**show) for show in get]

            for show in download_queue:
                sxe = 'S{:0>2}E{:0>2}'.format(show.episode['seasonNumber'], show.episode['episodeNumber'])
                if show.protocol.upper() == 'USENET':
                    protocol_id = 1
                else:
                    protocol_id = 0

                queue.append((show.series['title'], show.episode['title'], show.protocol.upper(),
                              protocol_id, sxe, show.id))

            for series_title, episode_title, protocol, protocol_id, sxe, sonarr_id in queue:
                influx_payload.append(
                    {
                        "measurement": "Sonarr",
                        "tags": {
                            "type": "Queue",
                            "sonarrId": sonarr_id,
                            "server": server.id

                        },
                        "time": self.now,
                        "fields": {
                            "name": series_title,
                            "epname": episode_title,
                            "sxe": sxe,
                            "protocol": protocol,
                            "protocol_id": protocol_id
                        }
                    }
                )

        self.influx_push(influx_payload)

    def influx_push(self, payload):
        # TODO: error handling for failed connection
        self.influx.write_points(payload)
