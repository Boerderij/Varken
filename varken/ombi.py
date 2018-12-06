import logging
from requests import Session, Request
from datetime import datetime, timezone

from varken.helpers import connection_handler
from varken.structures import OmbiRequestCounts


class OmbiAPI(object):
    def __init__(self, server, dbmanager):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'Apikey': self.server.api_key}
        self.logger = logging.getLogger()

    def __repr__(self):
        return "<ombi-{}>".format(self.server.id)

    def get_total_requests(self):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        tv_endpoint = '/api/v1/Request/tv'
        movie_endpoint = "/api/v1/Request/movie"

        tv_req = self.session.prepare_request(Request('GET', self.server.url + tv_endpoint))
        movie_req = self.session.prepare_request(Request('GET', self.server.url + movie_endpoint))
        get_tv = connection_handler(self.session, tv_req, self.server.verify_ssl)
        get_movie = connection_handler(self.session, movie_req, self.server.verify_ssl)

        if not all([get_tv, get_movie]):
            return

        movie_requests = len(get_movie)
        tv_requests = len(get_tv)

        influx_payload = [
            {
                "measurement": "Ombi",
                "tags": {
                    "type": "Request_Total"
                },
                "time": self.now,
                "fields": {
                    "total": movie_requests + tv_requests,
                    "movies": movie_requests,
                    "tv_shows": tv_requests
                }
            }
        ]

        self.dbmanager.write_points(influx_payload)

    def get_request_counts(self):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = '/api/v1/Request/count'

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        requests = OmbiRequestCounts(**get)
        influx_payload = [
            {
                "measurement": "Ombi",
                "tags": {
                    "type": "Request_Counts"
                },
                "time": self.now,
                "fields": {
                    "pending": requests.pending,
                    "approved": requests.approved,
                    "available": requests.available
                }
            }
        ]

        self.dbmanager.write_points(influx_payload)
