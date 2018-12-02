from requests import Session
from datetime import datetime, timezone

from Varken.helpers import OmbiRequestCounts
from Varken.logger import logging

class OmbiAPI(object):
    def __init__(self, server, dbmanager):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'Apikey': self.server.api_key}

    @logging
    def get_total_requests(self):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        tv_endpoint = '/api/v1/Request/tv'
        movie_endpoint = "/api/v1/Request/movie"
        get_tv = self.session.get(self.server.url + tv_endpoint, verify=self.server.verify_ssl).json()
        get_movie = self.session.get(self.server.url + movie_endpoint, verify=self.server.verify_ssl).json()

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

    @logging
    def get_request_counts(self):
        self.now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = '/api/v1/Request/count'
        get = self.session.get(self.server.url + endpoint, verify=self.server.verify_ssl).json()
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
