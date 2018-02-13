# Do not edit this script. Edit configuration.py
import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient

import configuration

current_time = datetime.now(timezone.utc).astimezone().isoformat()

headers = {'X-Api-Key': configuration.radarr_api_key}
get_movies = requests.get('{}/api/movie'.format(configuration.radarr_url),  headers=headers).json()
movies = {d['tmdbId']: d for d in get_movies}
missing = []
influx_payload = []

for movie in movies.keys():
    if not movies[movie]['downloaded']:
        missing.append((movies[movie]['title'], movies[movie]['tmdbId']))

for movie, id in missing:
    influx_payload.append(
        {
            "measurement": "Radarr",
            "tags": {
                "type": "Missing",
                "tmdbId": id
            },
            "time": current_time,
            "fields": {
                "name": movie
            }
        }
    )

influx = InfluxDBClient(configuration.grafana_url, configuration.grafana_port, configuration.grafana_username,
                        configuration.grafana_password, configuration.radarr_grafana_db_name)
influx.write_points(influx_payload)

