#!/usr/bin/env python3
# Do not edit this script. Edit configuration.py
import sys
import requests
import argparse
from influxdb import InfluxDBClient
from datetime import datetime, timezone, date, timedelta

from Varken import configuration as config
from Varken.helpers import Server, TVShow, Queue


class SonarrAPI(object):
    # Sets None as default for all TVShow NamedTuples, because sonarr's response json is inconsistent
    TVShow.__new__.__defaults__ = (None,) * len(TVShow._fields)

    def __init__(self):
        # Set Time of initialization
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.today = str(date.today())
        self.influx = InfluxDBClient(config.influxdb_url, config.influxdb_port, config.influxdb_username,
                                     config.influxdb_password, config.sonarr_influxdb_db_name)
        self.influx_payload = []
        self.servers = self.get_servers()
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = requests.Session()
        self.session.params = {'pageSize': 1000}

    @staticmethod
    def get_servers():
        # Ensure sonarr servers have been defined
        if not config.sonarr_server_list:
            sys.exit("No Sonarr servers defined in config")

        # Build Server Objects from config
        servers = []
        for url, api_key, server_id in config.sonarr_server_list:
            servers.append(Server(url=url, api_key=api_key, id=server_id))

        return servers

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

    def get_upcoming(self):
        endpoint = '/api/calendar/'

        for server in self.servers:
            upcoming = []
            headers = {'X-Api-Key': server.api_key}

            get = self.session.get(server.url + endpoint, headers=headers).json()
            tv_shows = [TVShow(**show) for show in get]

            for show in tv_shows:
                sxe = 'S{:0>2}E{:0>2}'.format(show.seasonNumber, show.episodeNumber)
                upcoming.append((show.series['title'], sxe, show.id, show.title, show.airDate))

            for series_title, sxe, sonarr_id, episode_title, air_date in upcoming:
                self.influx_payload.append(
                    {
                        "measurement": "Sonarr",
                        "tags": {
                            "type": "Soon",
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
    parser.add_argument("--upcoming", action='store_true', help='Get upcoming TV shows')
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
