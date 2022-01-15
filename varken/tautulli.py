from logging import getLogger
from requests import Session, Request
from geoip2.errors import AddressNotFoundError
from datetime import datetime, timezone, date, timedelta
from influxdb.exceptions import InfluxDBClientError

from varken.structures import TautulliStream
from varken.helpers import hashit, connection_handler, itemgetter_with_default


class TautulliAPI(object):
    def __init__(self, server, dbmanager, geoiphandler):
        self.dbmanager = dbmanager
        self.server = server
        self.geoiphandler = geoiphandler
        self.session = Session()
        self.session.params = {'apikey': self.server.api_key}
        self.endpoint = '/api/v2'
        self.logger = getLogger()
        self.my_ip = None

    def __repr__(self):
        return f"<tautulli-{self.server.id}>"

    def get_activity(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        params = {'cmd': 'get_activity'}

        req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
        g = connection_handler(self.session, req, self.server.verify_ssl)

        if not g:
            return

        get = g['response']['data']
        fields = itemgetter_with_default(**TautulliStream._field_defaults)

        try:
            sessions = [TautulliStream(*fields(session)) for session in get['sessions']]
        except TypeError as e:
            self.logger.error('TypeError has occurred : %s while creating TautulliStream structure', e)
            return

        for session in sessions:
            # Check to see if ip_address_public attribute exists as it was introduced in v2
            try:
                getattr(session, 'ip_address_public')
            except AttributeError:
                self.logger.error('Public IP attribute missing!!! Do you have an old version of Tautulli (v1)?')
                exit(1)

            try:
                geodata = self.geoiphandler.lookup(session.ip_address_public)
            except (ValueError, AddressNotFoundError):
                self.logger.debug('Public IP missing for Tautulli session...')
                if not self.my_ip:
                    # Try the fallback ip in the config file
                    try:
                        self.logger.debug('Attempting to use the fallback IP...')
                        geodata = self.geoiphandler.lookup(self.server.fallback_ip)
                    except AddressNotFoundError as e:
                        self.logger.error('%s', e)

                        self.my_ip = self.session.get('http://ip.42.pl/raw').text
                        self.logger.debug('Looked the public IP and set it to %s', self.my_ip)

                        geodata = self.geoiphandler.lookup(self.my_ip)

                else:
                    geodata = self.geoiphandler.lookup(self.my_ip)

            if not all([geodata.location.latitude, geodata.location.longitude]):
                latitude = 37.234332396
                longitude = -115.80666344
            else:
                latitude = geodata.location.latitude
                longitude = geodata.location.longitude

            if not geodata.city.name:
                location = '👽'
            else:
                location = geodata.city.name

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
            elif session.stream_video_full_resolution:
                quality = session.stream_video_full_resolution
            else:
                quality = session.stream_video_resolution + 'p'

            player_state = session.state.lower()
            if player_state == 'playing':
                player_state = 0
            elif player_state == 'paused':
                player_state = 1
            elif player_state == 'buffering':
                player_state = 3

            # Platform Version Overrides
            product_version = session.product_version
            if session.platform in ('Roku', 'osx', 'windows'):
                product_version = session.product_version.split('-')[0]

            # Platform Overrides
            platform_name = session.platform
            if platform_name in 'osx':
                platform_name = 'macOS'
            if platform_name in 'windows':
                platform_name = 'Windows'

            hash_id = hashit(f'{session.session_id}{session.session_key}{session.username}{session.full_title}')
            influx_payload.append(
                {
                    "measurement": "Tautulli",
                    "tags": {
                        "type": "Session",
                        "session_id": session.session_id,
                        "ip_address": session.ip_address,
                        "friendly_name": session.friendly_name,
                        "username": session.username,
                        "title": session.full_title,
                        "product": session.product,
                        "platform": platform_name,
                        "product_version": product_version,
                        "quality": quality,
                        "video_decision": video_decision.title(),
                        "transcode_decision": decision.title(),
                        "transcode_hw_decoding": session.transcode_hw_decoding,
                        "transcode_hw_encoding": session.transcode_hw_encoding,
                        "media_type": session.media_type.title(),
                        "audio_codec": session.audio_codec.upper(),
                        "audio_profile": session.audio_profile.upper(),
                        "stream_audio_codec": session.stream_audio_codec.upper(),
                        "quality_profile": session.quality_profile,
                        "progress_percent": session.progress_percent,
                        "region_code": geodata.subdivisions.most_specific.iso_code,
                        "location": location,
                        "full_location": f'{geodata.subdivisions.most_specific.name} - {geodata.city.name}',
                        "latitude": latitude,
                        "longitude": longitude,
                        "player_state": player_state,
                        "device_type": platform_name,
                        "relayed": session.relayed,
                        "secure": session.secure,
                        "server": self.server.id
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        influx_payload.append(
            {
                "measurement": "Tautulli",
                "tags": {
                    "type": "current_stream_stats",
                    "server": self.server.id
                },
                "time": now,
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

        self.dbmanager.write_points(influx_payload)

    def get_stats(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        params = {'cmd': 'get_libraries'}

        req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
        g = connection_handler(self.session, req, self.server.verify_ssl)

        if not g:
            return

        get = g['response']['data']

        for library in get:
            data = {
                    "measurement": "Tautulli",
                    "tags": {
                        "type": "library_stats",
                        "server": self.server.id,
                        "section_name": library['section_name'],
                        "section_type": library['section_type']
                    },
                    "time": now,
                    "fields": {
                        "total": int(library['count'])
                    }
            }
            if library['section_type'] == 'show':
                data['fields']['seasons'] = int(library['parent_count'])
                data['fields']['episodes'] = int(library['child_count'])

            elif library['section_type'] == 'artist':
                data['fields']['artists'] = int(library['count'])
                data['fields']['albums'] = int(library['parent_count'])
                data['fields']['tracks'] = int(library['child_count'])
            influx_payload.append(data)

        self.dbmanager.write_points(influx_payload)

    def get_historical(self, days=30):
        influx_payload = []
        start_date = date.today() - timedelta(days=days)
        params = {'cmd': 'get_history', 'grouping': 1, 'length': 1000000}
        req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
        g = connection_handler(self.session, req, self.server.verify_ssl)

        if not g:
            return

        get = g['response']['data']['data']

        params = {'cmd': 'get_stream_data', 'row_id': 0}
        sessions = []
        for history_item in get:
            if not history_item['id']:
                self.logger.debug('Skipping entry with no ID. (%s)', history_item['full_title'])
                continue
            if date.fromtimestamp(history_item['started']) < start_date:
                continue
            params['row_id'] = history_item['id']
            req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
            g = connection_handler(self.session, req, self.server.verify_ssl)
            if not g:
                self.logger.debug('Could not get historical stream data for %s. Skipping.', history_item['full_title'])
            try:
                self.logger.debug('Adding %s to history', history_item['full_title'])
                history_item.update(g['response']['data'])
                sessions.append(TautulliStream(**history_item))
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating TautulliStream structure', e)
                continue

        for session in sessions:
            try:
                geodata = self.geoiphandler.lookup(session.ip_address)
            except (ValueError, AddressNotFoundError):
                self.logger.debug('Public IP missing for Tautulli session...')
                if not self.my_ip:
                    # Try the fallback ip in the config file
                    try:
                        self.logger.debug('Attempting to use the fallback IP...')
                        geodata = self.geoiphandler.lookup(self.server.fallback_ip)
                    except AddressNotFoundError as e:
                        self.logger.error('%s', e)

                        self.my_ip = self.session.get('http://ip.42.pl/raw').text
                        self.logger.debug('Looked the public IP and set it to %s', self.my_ip)

                        geodata = self.geoiphandler.lookup(self.my_ip)

                else:
                    geodata = self.geoiphandler.lookup(self.my_ip)

            if not all([geodata.location.latitude, geodata.location.longitude]):
                latitude = 37.234332396
                longitude = -115.80666344
            else:
                latitude = geodata.location.latitude
                longitude = geodata.location.longitude

            if not geodata.city.name:
                location = '👽'
            else:
                location = geodata.city.name

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
            elif session.stream_video_full_resolution:
                quality = session.stream_video_full_resolution
            else:
                quality = session.stream_video_resolution + 'p'

            # Platform Overrides
            platform_name = session.platform
            if platform_name in 'osx':
                platform_name = 'Plex Mac OS'
            if platform_name in 'windows':
                platform_name = 'Plex Windows'

            player_state = 100

            hash_id = hashit(f'{session.id}{session.session_key}{session.user}{session.full_title}')
            influx_payload.append(
                {
                    "measurement": "Tautulli",
                    "tags": {
                        "type": "Session",
                        "session_id": session.session_id,
                        "ip_address": session.ip_address,
                        "friendly_name": session.friendly_name,
                        "username": session.user,
                        "title": session.full_title,
                        "product": session.product,
                        "platform": platform_name,
                        "quality": quality,
                        "video_decision": video_decision.title(),
                        "transcode_decision": decision.title(),
                        "transcode_hw_decoding": session.transcode_hw_decoding,
                        "transcode_hw_encoding": session.transcode_hw_encoding,
                        "media_type": session.media_type.title(),
                        "audio_codec": session.audio_codec.upper(),
                        "stream_audio_codec": session.stream_audio_codec.upper(),
                        "quality_profile": session.quality_profile,
                        "progress_percent": session.progress_percent,
                        "region_code": geodata.subdivisions.most_specific.iso_code,
                        "location": location,
                        "full_location": f'{geodata.subdivisions.most_specific.name} - {geodata.city.name}',
                        "latitude": latitude,
                        "longitude": longitude,
                        "player_state": player_state,
                        "device_type": platform_name,
                        "relayed": session.relayed,
                        "secure": session.secure,
                        "server": self.server.id
                    },
                    "time": datetime.fromtimestamp(session.stopped).astimezone().isoformat(),
                    "fields": {
                        "hash": hash_id
                    }
                }
            )
            try:
                self.dbmanager.write_points(influx_payload)
            except InfluxDBClientError as e:
                if "beyond retention policy" in str(e):
                    self.logger.debug('Only imported 30 days of data per retention policy')
                else:
                    self.logger.error('Something went wrong... post this output in discord: %s', e)
