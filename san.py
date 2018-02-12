import requests
import psutil
import mdstat

from datetime import datetime, timezone, timedelta

from influxdb import InfluxDBClient

# noinspection PyUnresolvedReferences
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

raid6 = psutil.disk_usage('/mnt')

influx_payload = [
    {
        "measurement": "Storage Servers",
        "tags": {
            "server": "SAN2"
        },
        "time": datetime.now(timezone.utc).astimezone().isoformat(),
        "fields": {
            "Name": '/mnt',
            "bytes Used": raid6.used,
            "bytes Free": raid6.free,
            "bytes Total": raid6.total,
            "Utilization": raid6.percent,
            "Non Degraded Disks":  mdstat.parse()['devices']['md127']['status']['raid_disks'] /  mdstat.parse()['devices']['md127']['status']['non_degraded_disks'] * 100,
            "IO_Wait": psutil.cpu_times_percent().iowait
        }
    }
]

influx = InfluxDBClient('grafana.domain.tld', 8086, 'root', 'root', 'storage_server')
influx.write_points(influx_payload)
