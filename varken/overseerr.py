from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.helpers import connection_handler, hashit
from varken.structures import OverseerrRequestCounts


class OverseerrAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'X-Api-Key': self.server.api_key}
        self.logger = getLogger()

    def __repr__(self):
        return f"<overseerr-{self.server.id}>"

    def get_request_counts(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = '/api/v1/request/count'

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get_req = connection_handler(self.session, req, self.server.verify_ssl)

        if not get_req:
            return

        requests = OverseerrRequestCounts(**get_req)
        influx_payload = [
            {
                "measurement": "Overseerr",
                "tags": {
                    "type": "Request_Counts"
                },
                "time": now,
                "fields": {
                    "pending": requests.pending,
                    "approved": requests.approved,
                    "processing": requests.processing,
                    "available": requests.available,
                    "total": requests.total,
                    "movies": requests.movie,
                    "tv": requests.tv,
                    "declined": requests.declined
                }
            }
        ]

        if influx_payload:
            self.dbmanager.write_points(influx_payload)
        else:
            self.logger.warning("No data to send to influx for overseerr-request-counts instance, discarding.")

    def get_latest_requests(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = '/api/v1/request?take=' + str(self.server.num_latest_requests_to_fetch) + '&filter=all&sort=added'
        movie_endpoint = '/api/v1/movie/'
        tv_endpoint = '/api/v1/tv/'

        # GET THE LATEST n REQUESTS
        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get_latest_req = connection_handler(self.session, req, self.server.verify_ssl)

        # RETURN NOTHING IF NO RESULTS
        if not get_latest_req:
            self.logger.warning("No data to send to influx for overseerr-latest-requests instance, discarding.")
            return

        influx_payload = []

        # Request Type: Movie = 1, TV Show = 0
        for result in get_latest_req['results']:
            if result['type'] == 'tv':
                req = self.session.prepare_request(Request('GET',
                                                           self.server.url +
                                                           tv_endpoint +
                                                           str(result['media']['tmdbId'])))
                get_tv_req = connection_handler(self.session, req, self.server.verify_ssl)
                hash_id = hashit(f'{get_tv_req["id"]}{get_tv_req["name"]}')

                influx_payload.append(
                    {
                        "measurement": "Overseerr",
                        "tags": {
                            "type": "Requests",
                            "server": self.server.id,
                            "request_type": 0,
                            "status": get_tv_req['mediaInfo']['status'],
                            "title": get_tv_req['name'],
                            "requested_user": get_tv_req['mediaInfo']['requests'][0]['requestedBy']['displayName'],
                            "requested_date": get_tv_req['mediaInfo']['requests'][0]['createdAt']
                        },
                        "time": now,
                        "fields": {
                            "hash": hash_id
                        }
                    }
                )

            if result['type'] == 'movie':
                req = self.session.prepare_request(Request('GET',
                                                           self.server.url +
                                                           movie_endpoint +
                                                           str(result['media']['tmdbId'])))
                get_movie_req = connection_handler(self.session, req, self.server.verify_ssl)
                hash_id = hashit(f'{get_movie_req["id"]}{get_movie_req["title"]}')

                influx_payload.append(
                    {
                        "measurement": "Overseerr",
                        "tags": {
                            "type": "Requests",
                            "server": self.server.id,
                            "request_type": 1,
                            "status": get_movie_req['mediaInfo']['status'],
                            "title": get_movie_req['title'],
                            "requested_user": get_movie_req['mediaInfo']['requests'][0]['requestedBy']['displayName'],
                            "requested_date": get_movie_req['mediaInfo']['requests'][0]['createdAt']
                        },
                        "time": now,
                        "fields": {
                            "hash": hash_id
                        }
                    }
                )

        if influx_payload:
            self.dbmanager.write_points(influx_payload)
        else:
            self.logger.warning("No data to send to influx for overseerr-latest-requests instance, discarding.")
