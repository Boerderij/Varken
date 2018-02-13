# Do not edit this script. Edit configuration.py
import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient

import configuration

current_time = datetime.now(timezone.utc).astimezone().isoformat()
headers = {'X-Api-Key': configuration.sonarr_api_key}
get_tv_shows = requests.get('{}/api/wanted/missing/?pageSize=1000'.format(configuration.sonarr_url),
                            headers=headers).json()['records']
tv_shows = {d['id']: d for d in get_tv_shows}
missing = []
influx_payload = []

for show in tv_shows.keys():
    name = '{} - S{}E{}'.format(tv_shows[show]['series']['title'], tv_shows[show]['seasonNumber'],
                                tv_shows[show]['episodeNumber'])
    missing.append((name, tv_shows[show]['id']))

for show, id in missing:
    influx_payload.append(
        {
            "measurement": "Sonarr",
            "tags": {
                "type": "Missing",
                "sonarrId": id
            },
            "time": current_time,
            "fields": {
                "name": show
            }
        }
    )

influx = InfluxDBClient(configuration.grafana_url, configuration.grafana_port, configuration.grafana_username,
                        configuration.grafana_password, configuration.sonarr_grafana_db_name)
influx.write_points(influx_payload)

