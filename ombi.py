# Do not edit this script. Edit configuration.py
import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient

import configuration

current_time = datetime.now(timezone.utc).astimezone().isoformat()

headers = {'Apikey': configuration.ombi_api_key}
get_tv_requests = requests.get('{}/api/v1/Request/tv'.format(configuration.ombi_url), headers=headers).json()
get_movie_requests = requests.get('{}/api/v1/Request/movie'.format(configuration.ombi_url), headers=headers).json()

count_movie_requests = 0
count_tv_requests = 0

for show in get_tv_requests:
    count_tv_requests += 1
    
for movie in get_movie_requests:
    count_movie_requests += 1

influx_payload = [
    {
        "measurement": "Ombi",
        "tags": {
            "type": "Requests"
        },
        "time": current_time,
        "fields": {
            "total": count_movie_requests + count_tv_requests
        }
    }
]

influx = InfluxDBClient(configuration.grafana_url, configuration.grafana_port, configuration.grafana_username,
                        configuration.grafana_password, configuration.ombi_grafana_db_name)
influx.write_points(influx_payload)

