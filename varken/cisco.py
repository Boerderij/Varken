from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.helpers import connection_handler


class CiscoAPI(object):
    def __init__(self, firewall, dbmanager):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.dbmanager = dbmanager
        self.firewall = firewall
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.auth = (self.firewall.username, self.firewall.password)
        self.logger = getLogger()

        self.get_token()

    def __repr__(self):
        return f"<ciscoasa-{self.firewall.id}>"

    def get_token(self):
        endpoint = '/api/tokenservices'

        req = self.session.prepare_request(Request('POST', self.firewall.url + endpoint))
        post = connection_handler(self.session, req, self.firewall.verify_ssl)

        if not post:
            return

        self.session.headers = {'X-Auth-Token': post}

    def get_bandwidth(self):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = '/api/monitoring/device/interfaces/' + self.firewall.outside_interface

        if not self.session.headers:
            return

        req = self.session.prepare_request(Request('GET', self.firewall.url + endpoint))
        get = connection_handler(self.session, req, self.firewall.verify_ssl)

        if not get:
            return

        influx_payload = [
            {
                "measurement": "Cisco ASA",
                "tags": {
                    "interface": self.firewall.outside_interface
                },
                "time": self.now,
                "fields": {
                    "upload_bitrate": get['outputBitRate'],
                    "download_bitrate": get['inputBitRate']
                }
            }
        ]

        self.dbmanager.write_points(influx_payload)
