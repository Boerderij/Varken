import psutil
import mdstat
import platform
from datetime import datetime, timezone, timedelta
from influxdb import InfluxDBClient

# Do not edit below this line #
influx_payload = []
devices = {
    'md': mdstat.parse()['devices'],
}

for array in devices['md']:
    influx_payload.append(
        {
            "measurement": "Storage Servers",
            "tags": {
                "server": platform.uname()[1],
                "mount_point": array,
                "type": 'rebuild'
            },
            "time": datetime.now(timezone.utc).astimezone().isoformat(),
            "fields": {
                "resync_progress": float(devices['md'][array]['resync']['progress'].replace('%', '')),
                "resync_eta_mins": float(devices['md'][array]['resync']['finish'].replace('min', '')),
                "resync_eta_date": '{:%A, %b %d %I:%M %p}'.format(
                    datetime.now() + timedelta(minutes=float(devices['md'][array]['resync']['finish']
                                                             .replace('min', '')))),
                "resync_speed_KiB/s": int(devices['md'][array]['resync']['speed'].replace('K/sec', '')),
            }
        }
    )

influx = InfluxDBClient('grafana.domain.tld', 8086, 'root', 'root', 'storage_server')
influx.write_points(influx_payload)
