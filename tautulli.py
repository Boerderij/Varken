# Do not edit this script. Edit configuration.py
import os
import shutil
import tarfile
import requests
import urllib.request
import geoip2.database
from datetime import datetime, timezone
from influxdb import InfluxDBClient

import configuration

current_time = datetime.now(timezone.utc).astimezone().isoformat()

payload = {'apikey': configuration.tautulli_api_key, 'cmd': 'get_activity'}

activity = requests.get('{}/api/v2'.format(configuration.tautulli_url), params=payload).json()['response']['data']

sessions = {d['session_id']: d for d in activity['sessions']}


def GeoLite2db(ipaddress):
    dbfile = 'GeoLite2-City.mmdb'

    if not os.path.isfile('GeoLite2-City.mmdb'):
        urllib.request.urlretrieve('http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz', 'GeoLite2-City.tar.gz')
        tar = tarfile.open('GeoLite2-City.tar.gz', "r:gz")
        tar.extractall()
        tar.close()
        tempfolder = next(d for d in os.listdir(os.getcwd()) if 'GeoLite2' in d)
        tempfullpath = os.path.join(tempfolder, dbfile)
        os.rename(tempfullpath, dbfile)
        shutil.rmtree(tempfolder)

    reader = geoip2.database.Reader(dbfile)
    geodata = reader.city(ipaddress)

    return geodata


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
    try:
        geodata = GeoLite2db(sessions[session]['ip_address_public'])
    except ValueError:
        if configuration.tautulli_failback_ip:
            geodata =GeoLite2db(configuration.tautulli_failback_ip)
        else:
            geodata = GeoLite2db(requests.get('http://ip.42.pl/raw').text)

    decision = sessions[session]['transcode_decision']
    if decision == 'copy':
        decision = 'direct stream'

    influx_payload.append(
        {
            "measurement": "Tautulli",
            "tags": {
                "type": "Session",
                "region_code": geodata.subdivisions.most_specific.iso_code,
                "session_key": sessions[session]['session_key']
            },
            "time": current_time,
            "fields": {
                "name": sessions[session]['friendly_name'],
                "title": sessions[session]['full_title'],
                "quality": '{}p'.format(sessions[session]['video_resolution']),
                "video_decision": sessions[session]['stream_video_decision'],
                "transcode_decision": decision.title(),
                "platform": sessions[session]['platform'],
                "product_version": sessions[session]['product_version'],
                "quality_profile": sessions[session]['quality_profile'],
                "location": geodata.city.name,
            }
        }
    )

influx = InfluxDBClient(configuration.influxdb_url, configuration.influxdb_port, configuration.influxdb_username,
                        configuration.influxdb_password, configuration.tautulli_influxdb_db_name)
influx.write_points(influx_payload)
