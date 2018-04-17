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
    seriesTitle = '{}'.format(tv_shows[show]['series']['title'])
    sxe = 'S{:0>2} - E{:0>2}'.format(tv_shows[show]['seasonNumber'],tv_shows[show]['episodeNumber'])
    missing.append((seriesTitle, sxe, tv_shows[show]['id'], tv_shows[show]['title']))

for seriesTitle, sxe, id, title in missing:
    influx_payload.append(
        {
            "measurement": "Sonarr",
            "tags": {
                "type": "Missing",
                "sonarrId": id
            },
            "time": current_time,
            "fields": {
                "name": seriesTitle,
                "epname": title,
                "sxe": sxe
            }
        }
    )
    
get_upcoming_shows = requests.get('{}/api/calendar/'.format(configuration.sonarr_url),
                                  headers=headers).json()
upcoming_shows = {d['id']: d for d in get_upcoming_shows}
upcoming = []
influx_payload2 = []

for show in upcoming_shows.keys():
    seriesTitle = '{}'.format(upcoming_shows[show]['series']['title'])
    sxe = 'S{:0>2} - E{:0>2}'.format(upcoming_shows[show]['seasonNumber'],upcoming_shows[show]['episodeNumber'])
    upcoming.append((seriesTitle, sxe, upcoming_shows[show]['id'], upcoming_shows[show]['title'], upcoming_shows[show]['airDate']))

for seriesTitle, sxe, id, title, airDate  in upcoming:
    influx_payload2.append(
        {
            "measurement": "Sonarr",
            "tags": {
                 "type": "Soon",
                 "sonarrId": id
             },
             "time": current_time,
             "fields": {
                 "name": seriesTitle,
                 "epname": title,
                 "sxe": sxe,
                 "airs": airDate
             }
         }
    )

influx = InfluxDBClient(configuration.grafana_url, configuration.grafana_port, configuration.grafana_username,
                        configuration.grafana_password, configuration.sonarr_grafana_db_name)
influx.write_points(influx_payload)
influx.write_points(influx_payload2)
