# Do not edit this script. Edit configuration.py
import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient

import configuration

current_time = datetime.now(timezone.utc).astimezone().isoformat()
get_tv_shows = requests.get('{0}/api/{1}/?cmd=future&sort=date&type=missed|today|soon'.format(configuration.sickrage_url, configuration.sickrage_api_key)).json()['data']

influx_payload = []

for show in get_tv_shows['missed']:
    influx_payload.append(
        {
            "measurement": "Sickrage",
            "tags": {
                "type": "Missing",
                "tvdbid": show['tvdbid']
            },
            "time": current_time,
            "fields": {
                "name": show['show_name'],
                "epname": show['ep_name'],
                "epnum": show['episode'],
                "season": show['season'],
                "sxe": "S"+str(show['season']) + " - E" + str(show['episode']),
                "airs": show['airs']
                #"tvdbid": show['tvdbid']
            }
        }
    )

for show in get_tv_shows['soon']:
    influx_payload.append(
        {
            "measurement": "Sickrage",
            "tags": {
                "type": "Soon",
                "tvdbid": show['tvdbid']
            },
            "time": current_time,
            "fields": {
                "name": show['show_name'],
                "epname": show['ep_name'],
                "epnum": show['episode'],
                "season": show['season'],
                "sxe": "S"+str(show['season']) + " - E" + str(show['episode']),
                "airs": show['airs']
                #"tvdbid": show['tvdbid']
            }
        }
    )

influx = InfluxDBClient(configuration.grafana_url, configuration.grafana_port, configuration.grafana_username,
                        configuration.grafana_password, configuration.sickrage_grafana_db_name)
influx.write_points(influx_payload)
