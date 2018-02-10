import requests

from datetime import datetime, timezone

from influxdb import InfluxDBClient

# noinspection PyUnresolvedReferences
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

current_time = datetime.now(timezone.utc).astimezone().isoformat()

stats = {
    "name": 'router',
    "ip": 'X.X.X.X'
}

stats['token'] = requests.post('https://{}/api/tokenservices'.format(stats['ip']), auth=('username', 'password'),
                               verify=False)
stats['headers'] = {'X-Auth-Token': stats['token'].headers['X-Auth-Token']}
stats['outside_interface'] = requests.get('https://{}/api/monitoring/device/interfaces/Outside'.format(stats['ip']),
                                          headers=stats['headers'], verify=False).json()

influx_payload = [
    {
        "measurement": "bandwidth",
        "tags": {
            "interface": "outside"
        },
        "time": current_time,
        "fields": {
            "upload_bitrate": stats['outside_interface']['outputBitRate'],
            "download_bitrate": stats['outside_interface']['inputBitRate']
        }
    }
]

influx = InfluxDBClient('grafana.domain.tld', 8086, 'root', 'root', 'firewall')
influx.write_points(influx_payload)


