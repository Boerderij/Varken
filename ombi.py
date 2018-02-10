import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient

# noinspection PyUnresolvedReferences
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

current_time = datetime.now(timezone.utc).astimezone().isoformat()

headers = {'Apikey': 'xxxxxxxxxxxxxxxxxxxxxxx'}
get_tv_requests = requests.get('https://request.domain.tld/api/v1/Request/tv', headers=headers).json()
get_movie_requests = requests.get('https://request.domain.tld/api/v1/Request/movie', headers=headers).json()

count_movie_requests = 0
count_tv_requests = 0

for show in get_tv_requests:
    count_tv_requests +=1
    
for movie in get_movie_requests:
    count_movie_requests +=1

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

influx = InfluxDBClient('grafana.domain.tld', 8086, 'root', 'root', 'plex')
influx.write_points(influx_payload)

