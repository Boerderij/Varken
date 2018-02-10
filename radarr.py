import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient

# noinspection PyUnresolvedReferences
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

current_time = datetime.now(timezone.utc).astimezone().isoformat()

api_key = 'xxxxxxxxxxxxxxxxxxxxxxxx'
headers = {'X-Api-Key': api_key}
get_movies = requests.get('https://radarr.domain.tld/api/movie',  headers=headers).json()
movies = {d['tmdbId']: d for d in get_movies}
missing = []
influx_payload = []

for movie in movies.keys():
    if not movies[movie]['downloaded']:
        missing.append((movies[movie]['title'], movies[movie]['tmdbId']))

for movie, id in missing:
    influx_payload.append(
        {
            "measurement": "Plex",
            "tags": {
                "server": "Radarr",
                "type": "Missing",
                "tmdbId": id
            },
            "time": current_time,
            "fields": {
                "name": movie
            }
        }
    )


influx = InfluxDBClient('grafana.domain.tld', 8086, 'root', 'root', 'plex')
influx.write_points(influx_payload)

