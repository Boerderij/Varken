import os
import tarfile
import urllib.request
import time
from datetime import datetime, timezone
import geoip2.database
from influxdb import InfluxDBClient
import requests
import configuration

CURRENT_TIME = datetime.now(timezone.utc).astimezone().isoformat()

PAYLOAD = {'apikey': configuration.tautulli_api_key, 'cmd': 'get_activity'}

ACTIVITY = requests.get('{}/api/v2'.format(configuration.tautulli_url),
                        params=PAYLOAD).json()['response']['data']

SESSIONS = {d['session_id']: d for d in ACTIVITY['sessions']}

TAR_DBFILE = '{}/GeoLite2-City.tar.gz'.format(os.path.dirname(os.path.realpath(__file__)))

DBFILE = '{}/GeoLite2-City.mmdb'.format(os.path.dirname(os.path.realpath(__file__)))

NOW = time.time()

DB_AGE = NOW - (86400 * 35)

#remove the running db file if it is older than 35 days
try:
    t = os.stat(DBFILE)
    c = t.st_ctime
    if c < DB_AGE:
        os.remove(DBFILE)
except FileNotFoundError:
    pass


def geo_lookup(ipaddress):
    """Lookup an IP using the local GeoLite2 DB"""
    if not os.path.isfile(DBFILE):
        urllib.request.urlretrieve(
            'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz',
            TAR_DBFILE)

        tar = tarfile.open(TAR_DBFILE, "r:gz")
        for files in tar.getmembers():
            if 'GeoLite2-City.mmdb' in files.name:
                files.name = os.path.basename(files.name)
                tar.extract(files, '{}/'.format(os.path.dirname(os.path.realpath(__file__))))

    reader = geoip2.database.Reader(DBFILE)

    return reader.city(ipaddress)


INFLUX_PAYLOAD = [
    {
        "measurement": "Tautulli",
        "tags": {
            "type": "stream_count"
        },
        "time": CURRENT_TIME,
        "fields": {
            "current_streams": int(ACTIVITY['stream_count']),
            "transcode_streams": int(ACTIVITY['stream_count_transcode']),
            "direct_play_streams": int(ACTIVITY['stream_count_direct_play']),
            "direct_streams": int(ACTIVITY['stream_count_direct_stream'])
        }
    }
]

for session in SESSIONS.keys():
    try:
        geodata = geo_lookup(SESSIONS[session]['ip_address_public'])
    except (ValueError, geoip2.errors.AddressNotFoundError):
        if configuration.tautulli_failback_ip:
            geodata = geo_lookup(configuration.tautulli_failback_ip)
        else:
            geodata = geo_lookup(requests.get('http://ip.42.pl/raw').text)

    latitude = geodata.location.latitude

    if not geodata.location.latitude:
        latitude = 37.234332396
    else:
        latitude = geodata.location.latitude

    if not geodata.location.longitude:
        longitude = -115.80666344
    else:
        longitude = geodata.location.longitude

    decision = SESSIONS[session]['transcode_decision']

    if decision == 'copy':
        decision = 'direct stream'

    video_decision = SESSIONS[session]['stream_video_decision']

    if video_decision == 'copy':
        video_decision = 'direct stream'

    elif video_decision == '':
        video_decision = 'Music'

    quality = SESSIONS[session]['stream_video_resolution']


    # If the video resolution is empty. Asssume it's an audio stream
    # and use the container for music
    if not quality:
        quality = SESSIONS[session]['container'].upper()

    elif quality in ('SD', 'sd'):
        quality = SESSIONS[session]['stream_video_resolution'].upper()

    elif quality in '4k':
        quality = SESSIONS[session]['stream_video_resolution'].upper()

    else:
        quality = '{}p'.format(SESSIONS[session]['stream_video_resolution'])


    # Translate player_state to integers so we can colorize the table
    player_state = SESSIONS[session]['state'].lower()

    if player_state == 'playing':
        player_state = 0

    elif player_state == 'paused':
        player_state = 1

    elif player_state == 'buffering':
        player_state = 3


    INFLUX_PAYLOAD.append(
        {
            "measurement": "Tautulli",
            "tags": {
                "type": "Session",
                "session_id": SESSIONS[session]['session_id'],
                "name": SESSIONS[session]['friendly_name'],
                "title": SESSIONS[session]['full_title'],
                "platform": SESSIONS[session]['platform'],
                "product_version": SESSIONS[session]['product_version'],
                "quality": quality,
                "video_decision": video_decision.title(),
                "transcode_decision": decision.title(),
                "media_type": SESSIONS[session]['media_type'].title(),
                "audio_codec": SESSIONS[session]['audio_codec'].upper(),
                "audio_profile": SESSIONS[session]['audio_profile'].upper(),
                "stream_audio_codec": SESSIONS[session]['stream_audio_codec'].upper(),
                "quality_profile": SESSIONS[session]['quality_profile'],
                "progress_percent": SESSIONS[session]['progress_percent'],
                "region_code": geodata.subdivisions.most_specific.iso_code,
                "location": geodata.city.name,
                "full_location": '{} - {}'.format(geodata.subdivisions.most_specific.name,
                                                  geodata.city.name),
                "latitude": latitude,
                "longitude": longitude,
                "player_state": player_state,
                "device_type": SESSIONS[session]['platform']
            },
            "time": CURRENT_TIME,
            "fields": {
                "session_id": SESSIONS[session]['session_id'],
                "session_key": SESSIONS[session]['session_key']
            }
        }
    )

INFLUX_SENDER = InfluxDBClient(configuration.influxdb_url,
                               configuration.influxdb_port,
                               configuration.influxdb_username,
                               configuration.influxdb_password,
                               configuration.tautulli_influxdb_db_name)

INFLUX_SENDER.write_points(INFLUX_PAYLOAD)
