import platform
import psutil
from datetime import datetime, timezone
from influxdb import InfluxDBClient

mount_points = ['/mnt/raid6-a', '/mnt/raid6-b']

# Do not edit below this line #
influx_payload = []
devices = {
    'mount_points': {}
}

for mount in mount_points:
    devices['mount_points'][mount] = {
        'usage': psutil.disk_usage(mount)
    }
    influx_payload.append(
        {
            "measurement": "Storage Servers",
            "tags": {
                "server": platform.uname()[1],
                "mount_point": mount
            },
            "time": datetime.now(timezone.utc).astimezone().isoformat(),
            "fields": {
                "bytes Used": devices['mount_points'][mount]['usage'].used,
                "bytes Free": devices['mount_points'][mount]['usage'].free,
                "bytes Total": devices['mount_points'][mount]['usage'].total,
                "Utilization": devices['mount_points'][mount]['usage'].percent
            }
        }
    )

influx = InfluxDBClient('grafana.domain.tld', 8086, 'root', 'root', 'storage_server')
influx.write_points(influx_payload)
