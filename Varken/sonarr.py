#!/usr/bin/env python3
# Do not edit this script. Edit configuration.py
import sys
import requests
import argparse
from influxdb import InfluxDBClient
from datetime import datetime, timezone, date, timedelta

from Varken.helpers import TVShow, Queue


class SonarrAPI(object):
    def __init__(self, sonarr_servers, influx_server):
        # Set Time of initialization
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.today = str(date.today())
        self.influx = InfluxDBClient(influx_server.url, influx_server.port, influx_server.username,
                                     influx_server.password, 'plex')
        self.influx_payload = []
        self.servers = sonarr_servers
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = requests.Session()
        self.session.params = {'pageSize': 1000}

    def get_missing(self, days_past):
        endpoint = '/api/calendar'
        last_days = str(date.today() + timedelta(days=-days_past))
        params = {'start': last_days, 'end': self.today}

        for server in self.servers:
            missing = []
            headers = {'X-Api-Key': server.api_key}

            get = self.session.get(server.url + endpoint, params=params, headers=headers).json()
            # Iteratively create a list of TVShow Objects from response json
            tv_shows = [TVShow(**show) for show in get]

            # Add show to missing list if file does not exist
            for show in tv_shows:
                if not show.hasFile:
                    sxe = 'S{:0>2}E{:0>2}'.format(show.seasonNumber, show.episodeNumber)
                    missing.append((show.series['title'], sxe, show.airDate, show.title, show.id))

            for series_title, sxe, air_date, episode_title, sonarr_id in missing:
                self.influx_payload.append(
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

    def get_future(self, future_days):
        endpoint = '/api/calendar/'
        future = str(date.today() + timedelta(days=future_days))

        for server in self.servers:
            air_days = []
            headers = {'X-Api-Key': server.api_key}
            params = {'start': self.today, 'end': future}

            get = self.session.get(server.url + endpoint, params=params, headers=headers).json()
            tv_shows = [TVShow(**show) for show in get]

            for show in tv_shows:
                sxe = 'S{:0>2}E{:0>2}'.format(show.seasonNumber, show.episodeNumber)
                air_days.append((show.series['title'], show.hasFile, sxe, show.title, show.airDate, show.id))

            for series_title, dl_status, sxe, episode_title, air_date, sonarr_id in air_days:
                self.influx_payload.append(
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

    def get_queue(self):
        endpoint = '/api/queue'

        for server in self.servers:
            queue = []
            headers = {'X-Api-Key': server.api_key}

            get = self.session.get(server.url + endpoint, headers=headers).json()
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
                self.influx_payload.append(
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

    def influx_push(self):
        # TODO: error handling for failed connection
        self.influx.write_points(self.influx_payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Sonarr stats operations',
                                     description='Script to aid in data gathering from Sonarr',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--missing", metavar='$days', type=int,
                        help='Get missing TV shows in past X days'
                        '\ni.e. --missing 7 is in the last week')
    parser.add_argument("--missing_days", metavar='$days', type=int,
                        help='legacy command. Deprecated in favor of --missing'
                        '\nfunctions identically to --missing'
                        '\nNote: Will be removed in a future release')
    parser.add_argument("--future", metavar='$days', type=int,
                        help='Get TV shows on X days into the future. Includes today.'
                        '\ni.e. --future 2 is Today and Tomorrow')
    parser.add_argument("--queue", action='store_true', help='Get TV shows in queue')

    opts = parser.parse_args()
    sonarr = SonarrAPI()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if any([opts.missing, opts.missing_days]):
        days = opts.missing if opts.missing else opts.missing_days
        sonarr.get_missing(days)
    if opts.upcoming:
        sonarr.get_upcoming()
    if opts.future:
        sonarr.get_future(opts.future)
    if opts.queue:
        sonarr.get_queue()

    sonarr.influx_push()
