from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.helpers import connection_handler


class UniFiAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        self.site = self.server.site
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.logger = getLogger()
        self.get_retry = True
        self.get_cookie()
        self.get_site()

    def __repr__(self):
        return f"<unifi-{self.server.id}>"

    def get_cookie(self):
        endpoint = '/api/login'
        pre_cookies = {'username': self.server.username, 'password': self.server.password, 'remember': True}
        req = self.session.prepare_request(Request('POST', self.server.url + endpoint, json=pre_cookies))
        post = connection_handler(self.session, req, self.server.verify_ssl, as_is_reply=True)

        if not post or not post.cookies.get('unifises'):
            self.logger.error(f"Could not retrieve session cookie from UniFi Controller")
            return

        cookies = {'unifises': post.cookies.get('unifises')}
        self.session.cookies.update(cookies)

    def get_site(self):
        endpoint = '/api/self/sites'
        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            self.logger.error(f"Could not get list of sites from UniFi Controller")
            return
        site = [site['name'] for site in get['data'] if site['name'].lower() == self.server.site.lower()
                or site['desc'].lower() == self.server.site.lower()]
        if site:
            self.site = site[0]
        else:
            self.logger.error(f"Could not map site {self.server.site} to a site id/alias")

    def get_usg_stats(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = f'/api/s/{self.site}/stat/device'
        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            if self.get_retry:
                self.get_retry = False
                self.logger.error("Attempting to reauthenticate for unifi-%s", self.server.id)
                self.get_cookie()
                self.get_usg_stats()
            else:
                self.get_retry = True
                self.logger.error("Disregarding Job get_usg_stats for unifi-%s", self.server.id)
            return

        if not self.get_retry:
            self.get_retry = True

        devices = {device['name']: device for device in get['data'] if device.get('name')}

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
                        "cpu_loadavg_1": float(device['sys_stats']['loadavg_1']),
                        "cpu_loadavg_5": float(device['sys_stats']['loadavg_5']),
                        "cpu_loadavg_15": float(device['sys_stats']['loadavg_15']),
                        "cpu_util": float(device['system-stats']['cpu']),
                        "mem_util": float(device['system-stats']['mem']),
                    }
                }
            ]
            self.dbmanager.write_points(influx_payload)
        except KeyError as e:
            self.logger.error('Error building payload for unifi. Discarding. Error: %s', e)
