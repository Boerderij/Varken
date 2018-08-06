# Do not edit this script. Edit configuration.py
import sys
import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient
import argparse
from argparse import RawTextHelpFormatter
import configuration


def now_iso():
    now_iso = datetime.now(timezone.utc).astimezone().isoformat()
    return now_iso


def influx_sender(influx_payload):
    influx = InfluxDBClient(configuration.influxdb_url, configuration.influxdb_port, configuration.influxdb_username,
                            configuration.influxdb_password, configuration.radarr_influxdb_db_name)
    influx.write_points(influx_payload)


def get_missing_movies():
    # Set the time here so we have one timestamp to work with
    now = now_iso()
    missing = []
    influx_payload = []

    for radarr_url, radarr_api_key, server_id in configuration.radarr_server_list:
        headers = {'X-Api-Key': radarr_api_key}
        get_movies = requests.get('{}/api/movie'.format(radarr_url),  headers=headers).json()
        movies = {d['tmdbId']: d for d in get_movies}

        for movie in movies.keys():
            if not movies[movie]['downloaded']:
                movie_name = ('{} ({})'.format(movies[movie]['title'], movies[movie]['year']))
                missing.append((movie_name, movies[movie]['tmdbId']))

        for movie, id in missing:
            influx_payload.append(
                {
                    "measurement": "Radarr",
                    "tags": {
                        "type": "Missing",
                        "tmdbId": id,
                        "server": server_id
                    },
                    "time": now,
                    "fields": {
                        "name": movie
                    }
                }
            )
        # Empty missing or else things get foo bared
        missing = []

    return influx_payload


def get_missing_avl():
    # Set the time here so we have one timestamp to work with
    now = now_iso()
    missing = []
    influx_payload = []

    for radarr_url, radarr_api_key, server_id in configuration.radarr_server_list:
        headers = {'X-Api-Key': radarr_api_key}
        get_movies = requests.get('{}/api/movie'.format(radarr_url),  headers=headers).json()
        movies = {d['tmdbId']: d for d in get_movies}

        for movie in movies.keys():
            if not movies[movie]['downloaded']:
                if movies[movie]['isAvailable'] is True:
                    movie_name = ('{} ({})'.format(movies[movie]['title'], movies[movie]['year']))
                    missing.append((movie_name, movies[movie]['tmdbId']))


        for movie, id in missing:
            influx_payload.append(
                {
                    "measurement": "Radarr",
                    "tags": {
                        "type": "Missing_Available",
                        "tmdbId": id,
                        "server": server_id
                    },
                    "time": now,
                    "fields": {
                        "name": movie,
                    }
                }
            )
        # Empty missing or else things get foo bared
        missing = []

    return influx_payload


def get_queue_movies():
    # Set the time here so we have one timestamp to work with
    now = now_iso()
    influx_payload = []
    queue = []

    for radarr_url, radarr_api_key, server_id in configuration.radarr_server_list:
        headers = {'X-Api-Key': radarr_api_key}
        get_movies = requests.get('{}/api/queue'.format(radarr_url),  headers=headers).json()
        queue_movies = {d['id']: d for d in get_movies}

        for movie in queue_movies.keys():
            name = '{} ({})'.format(queue_movies[movie]['movie']['title'], queue_movies[movie]['movie']['year'])
            quality = (queue_movies[movie]['quality']['quality']['name'])
            protocol = (queue_movies[movie]['protocol'].upper())

            if protocol == 'USENET':
                protocol_id = 1
            else:
                protocol_id = 0

            queue.append((name, queue_movies[movie]['id']))

        for movie, id in queue:
            influx_payload.append(
                {
                    "measurement": "Radarr",
                    "tags": {
                        "type": "Queue",
                        "tmdbId": id,
                        "server": server_id
                    },
                    "time": now,
                    "fields": {
                        "name": movie,
                        "quality": quality,
                        "protocol": protocol,
                        "protocol_id": protocol_id
                    }
                }
            )
        # Empty queue or else things get foo bared
        queue = []

    return influx_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Radarr stats operations',
        description='Script to aid in data gathering from Radarr', formatter_class=RawTextHelpFormatter)

    parser.add_argument("--missing",  action='store_true',
        help='Get missing movies')

    parser.add_argument("--missing_avl",  action='store_true',
        help='Get missing available movies')

    parser.add_argument("--queue",  action='store_true',
        help='Get movies in queue')

    opts = parser.parse_args()

    if opts.missing:
        influx_sender(get_missing_movies())

    elif opts.missing_avl:
        influx_sender(get_missing_avl())

    elif opts.queue:
        influx_sender(get_queue_movies())

    elif len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
