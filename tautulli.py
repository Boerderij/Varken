# Do not edit this script. Edit configuration.py
import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient

import configuration

current_time = datetime.now(timezone.utc).astimezone().isoformat()
payload = {'apikey': configuration.tautulli_api_key, 'cmd': 'get_activity'}
activity = requests.get('{}/api/v2'.format(configuration.tautulli_url), params=payload).json()['response']['data']

sessions = {d['session_id']: d for d in activity['sessions']}

influx_payload = [
    {
        "measurement": "Tautulli",
        "tags": {
            "type": "stream_count"
        },
        "time": current_time,
        "fields": {
            "current_streams": int(activity['stream_count'])
        }
    }
]

for session in sessions.keys():
    lookup = requests.get('http://freegeoip.net/json/{}'.format(sessions[session]['ip_address_public'])).json()
    influx_payload.append(
        {
            "measurement": "Tautulli",
            "tags": {
                "type": "Session",
                "region_code": lookup['region_code'],
                "name": sessions[session]['friendly_name']
            },
            "time": current_time,
            "fields": {
                "name": sessions[session]['friendly_name'],
                "title": sessions[session]['full_title'],
                "quality": '{}p'.format(sessions[session]['video_resolution']),
                "transcode_decision": sessions[session]['transcode_decision'],
                "location": lookup['city'],
            }
        }
    )

influx = InfluxDBClient(configuration.grafana_url, configuration.grafana_port, configuration.grafana_username,
                        configuration.grafana_password, configuration.tautulli_grafana_db_name)
influx.write_points(influx_payload)

