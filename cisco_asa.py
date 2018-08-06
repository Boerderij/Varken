# Do not edit this script. Edit configuration.py
import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient

import configuration

current_time = datetime.now(timezone.utc).astimezone().isoformat()

stats = {
    'token': requests.post('{}/api/tokenservices'.format(configuration.asa_url),
                           auth=(configuration.asa_username, configuration.asa_password), verify=False)
}
stats['headers'] = {'X-Auth-Token': stats['token'].headers['X-Auth-Token']}
stats['outside_interface'] = requests.get('{}/api/monitoring/device/interfaces/Outside'.format(configuration.asa_url),
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

influx = InfluxDBClient(configuration.influxdb_url, configuration.influxdb_port, configuration.influxdb_username,
                        configuration.influxdb_password, configuration.asa_influxdb_db_name)
influx.write_points(influx_payload)
