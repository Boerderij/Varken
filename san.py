import subprocess
import requests
import re
import psutil

from datetime import datetime, timezone

from influxdb import InfluxDBClient

# noinspection PyUnresolvedReferences
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

current_time = datetime.now(timezone.utc).astimezone().isoformat()

raid6 = psutil.disk_usage('/mnt')

influx_payload = [
    {
        "measurement": "Storage Servers",
        "tags": {
            "server": "SAN3"
        },
        "time": current_time,
        "fields": {
            "Name": '/mnt',
            "bytes Used": raid6.used,
            "bytes Free": raid6.free,
            "bytes Total": raid6.total,
            "Utilization": raid6.percent,
            "IO_Wait": psutil.cpu_times_percent().iowait
        }
    }
]

influx = InfluxDBClient('grafana.domain.tld', 8086, 'root', 'root', 'storage_server')
influx.write_points(influx_payload)

