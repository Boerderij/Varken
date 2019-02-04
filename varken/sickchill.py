from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.structures import SickChillTVShow
from varken.helpers import hashit, connection_handler


class SickChillAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.params = {'limit': 1000}
        self.endpoint = f"/api/{self.server.api_key}"
        self.logger = getLogger()

    def __repr__(self):
        return f"<sickchill-{self.server.id}>"

    def get_missing(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        params = {'cmd': 'future', 'paused': 1, 'type': 'missed|today|soon|later|snatched'}

        req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        try:
            for key, section in get['data'].items():
                get['data'][key] = [SickChillTVShow(**show) for show in section]
        except TypeError as e:
            self.logger.error('TypeError has occurred : %s while creating SickChillTVShow structure', e)
            return

        for key, section in get['data'].items():
            for show in section:
                sxe = f'S{show.season:0>2}E{show.episode:0>2}'
                hash_id = hashit(f'{self.server.id}{show.show_name}{sxe}')
                missing_types = [(0, 'future'), (1, 'later'), (2, 'soon'), (3, 'today'), (4, 'missed')]
                try:
                    influx_payload.append(
                        {
                            "measurement": "SickChill",
                            "tags": {
                                "type": [item[0] for item in missing_types if key in item][0],
                                "indexerid": show.indexerid,
                                "server": self.server.id,
                                "name": show.show_name,
                                "epname": show.ep_name,
                                "sxe": sxe,
                                "airdate": show.airdate,
                            },
                            "time": now,
                            "fields": {
                                "hash": hash_id
                            }
                        }
                    )
                except IndexError as e:
                    self.logger.error('Error building payload for sickchill. Discarding. Error: %s', e)

        if influx_payload:
            self.dbmanager.write_points(influx_payload)
