from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.helpers import connection_handler


class UniFiAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.logger = getLogger()

        self.get_cookie()

    def __repr__(self):
        return f"<unifi-{self.server.id}>"

    def get_cookie(self):
        endpoint = '/api/login'
        pre_cookies = {'username': self.server.username, 'password': self.server.password, 'remember': True}
        req = self.session.prepare_request(Request('POST', self.server.url + endpoint, json=pre_cookies))
        post = connection_handler(self.session, req, self.server.verify_ssl, as_is_reply=True)

        if not post.cookies.get('unifises'):
            return

        cookies = {'unifises': post.cookies.get('unifises')}
        self.session.cookies.update(cookies)

    def get_usg_stats(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = f'/api/s/{self.server.site}/stat/device'
        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            self.logger.error("Canceling Job get_usg_stats for unifi-%s", self.server.id)
            return f"unifi-{self.server.id}-get_usg_stats"

        devices = {device['name']: device for device in get['data']}
        if devices.get(self.server.usg_name):
            device = devices[self.server.usg_name]
        else:
            self.logger.error("Could not find a USG named %s from your UniFi Controller", self.server.usg_name)
            return

        try:
            influx_payload = [
                {
                    "measurement": "UniFi",
                    "tags": {
                        "model": device['model'],
                        "name": device['name']
                    },
                    "time": now,
                    "fields": {
                        "bytes_current": device['wan1']['bytes-r'],
                        "rx_bytes_total": device['wan1']['rx_bytes'],
                        "rx_bytes_current": device['wan1']['rx_bytes-r'],
                        "tx_bytes_total": device['wan1']['tx_bytes'],
                        "tx_bytes_current": device['wan1']['tx_bytes-r'],
                        # Commenting speedtest out until Unifi gets their shit together
                        # "speedtest_latency": device['speedtest-status']['latency'],
                        # "speedtest_download": device['speedtest-status']['xput_download'],
                        # "speedtest_upload": device['speedtest-status']['xput_upload'],
                        "cpu_loadavg_1": device['sys_stats']['loadavg_1'],
                        "cpu_loadavg_5": device['sys_stats']['loadavg_5'],
                        "cpu_loadavg_15": device['sys_stats']['loadavg_15'],
                        "cpu_util": device['system-stats']['cpu'],
                        "mem_util": device['system-stats']['mem'],
                    }
                }
            ]
            self.dbmanager.write_points(influx_payload)
        except KeyError as e:
            self.logger.error('Error building payload for unifi. Discarding. Error: %s', e)
