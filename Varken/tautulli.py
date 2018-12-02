from datetime import datetime, timezone
from geoip2.errors import AddressNotFoundError
from influxdb import InfluxDBClient
from requests import Session
from Varken.helpers import TautulliStream, geo_lookup
from Varken.logger import logging


class TautulliAPI(object):
    def __init__(self, server, influx_server):
        # Set Time of initialization
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.influx = InfluxDBClient(influx_server.url, influx_server.port, influx_server.username,
                                     influx_server.password, 'plex2')
        self.server = server
        self.session = Session()
        self.endpoint = '/api/v2'

    def influx_push(self, payload):
        self.influx.write_points(payload)

    @logging
    def get_activity(self):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        params = {'cmd': 'get_activity'}
        influx_payload = []
        params['apikey'] = self.server.api_key
        g = self.session.get(self.server.url + self.endpoint, params=params, verify=self.server.verify_ssl)
        get = g.json()['response']['data']

        influx_payload.append(
            {
                "measurement": "Tautulli",
                "tags": {
                    "type": "current_stream_stats",
                    "server": self.server.id
                },
                "time": self.now,
                "fields": {
                    "stream_count": int(get['stream_count']),
                    "total_bandwidth": int(get['total_bandwidth']),
                    "wan_bandwidth": int(get['wan_bandwidth']),
                    "lan_bandwidth": int(get['lan_bandwidth']),
                    "transcode_streams": int(get['stream_count_transcode']),
                    "direct_play_streams": int(get['stream_count_direct_play']),
                    "direct_streams": int(get['stream_count_direct_stream'])
                }
            }
        )

        self.influx_push(influx_payload)

    @logging
    def get_sessions(self):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        params = {'cmd': 'get_activity'}
        influx_payload = []
        params['apikey'] = self.server.api_key
        g = self.session.get(self.server.url + self.endpoint, params=params, verify=self.server.verify_ssl)
        get = g.json()['response']['data']['sessions']
        sessions = [TautulliStream(**session) for session in get]

        for session in sessions:
            try:
                geodata = geo_lookup(session.ip_address_public)
            except (ValueError, AddressNotFoundError):
                if self.server.fallback_ip:
                    geodata = geo_lookup(self.server.fallback_ip)
                else:
                    my_ip = self.session.get('http://ip.42.pl/raw').text
                    geodata = geo_lookup(my_ip)

            if not all([geodata.location.latitude, geodata.location.longitude]):
                latitude = 37.234332396
                longitude = -115.80666344
            else:
                latitude = geodata.location.latitude
                longitude = geodata.location.longitude

            decision = session.transcode_decision
            if decision == 'copy':
                decision = 'direct stream'

            video_decision = session.stream_video_decision
            if video_decision == 'copy':
                video_decision = 'direct stream'
            elif video_decision == '':
                video_decision = 'Music'

            quality = session.stream_video_resolution
            if not quality:
                quality = session.container.upper()
            elif quality in ('SD', 'sd', '4k'):
                quality = session.stream_video_resolution.upper()
            else:
                quality = session.stream_video_resolution + 'p'

            player_state = session.state.lower()
            if player_state == 'playing':
                player_state = 0
            elif player_state == 'paused':
                player_state = 1
            elif player_state == 'buffering':
                player_state = 3

            product_version = session.product_version
            if session.platform == 'Roku':
                product_version = session.product_version.split('-')[0]

            influx_payload.append(
                {
                    "measurement": "Tautulli",
                    "tags": {
                        "type": "Session",
                        "session_id": session.session_id,
                        "name": session.friendly_name,
                        "title": session.full_title,
                        "platform": session.platform,
                        "product_version": product_version,
                        "quality": quality,
                        "video_decision": video_decision.title(),
                        "transcode_decision": decision.title(),
                        "media_type": session.media_type.title(),
                        "audio_codec": session.audio_codec.upper(),
                        "audio_profile": session.audio_profile.upper(),
                        "stream_audio_codec": session.stream_audio_codec.upper(),
                        "quality_profile": session.quality_profile,
                        "progress_percent": session.progress_percent,
                        "region_code": geodata.subdivisions.most_specific.iso_code,
                        "location": geodata.city.name,
                        "full_location": '{} - {}'.format(geodata.subdivisions.most_specific.name,
                                                          geodata.city.name),
                        "latitude": latitude,
                        "longitude": longitude,
                        "player_state": player_state,
                        "device_type": session.platform,
                        "server": self.server.id
                    },
                    "time": self.now,
                    "fields": {
                        "session_id": session.session_id,
                        "session_key": session.session_key
                    }
                }
            )

        self.influx_push(influx_payload)
