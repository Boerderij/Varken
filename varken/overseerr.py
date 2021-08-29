from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.helpers import connection_handler, hashit
from varken.structures import OverseerrRequest, OverseerrRequestCounts


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

    def get_total_requests(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = '/api/v1/request?take=99999999999&filter=all&sort=added'

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get_req = connection_handler(self.session, req, self.server.verify_ssl) or []

        if not any([get_req]):
            self.logger.error('No json replies. Discarding job')
            return

        tv_requests = []
        movie_requests = []

        for result in get_req['results']:
            if result['type'] == 'tv':
                try:
                    tv_requests.append(OverseerrRequest(**result))
                except TypeError as e:
                    self.logger.error('TypeError has occurred : %s while creating OverseerrRequest structure for show. '
                                        'data attempted is: %s', e, result)
            
            if result['type'] == 'movie':
                try:
                    movie_requests.append(OverseerrRequest(**result))
                except TypeError as e:
                    self.logger.error('TypeError has occurred : %s while creating OverseerrRequest structure for movie. '
                                        'data attempted is: %s', e, result)

        if tv_requests:
            tv_request_count = len(tv_requests)

        if movie_requests:
            movie_request_count = len(movie_requests)

        influx_payload = [
            {
                "measurement": "Overseerr",
                "tags": {
                    "type": "Request_Totals",
                    "server": self.server.id
                },
                "time": now,
                "fields": {
                    "total": movie_request_count + tv_request_count,
                    "movies": movie_request_count,
                    "tv": tv_request_count
                }
            }
        ]

        if influx_payload:
            self.dbmanager.write_points(influx_payload)
        else:
            self.logger.debug("Empty dataset for overseerr module. Discarding...")

    def get_request_status_counts(self):
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
                    "available": requests.available
                }
            }
        ]

        self.dbmanager.write_points(influx_payload)

    def get_latest_requests(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = '/api/v1/request?take=' + str(self.server.num_latest_requests_to_fetch) + '&filter=all&sort=added'
        movie_endpoint = '/api/v1/movie/'
        tv_endpoint = '/api/v1/tv/'

        #GET THE LATEST n REQUESTS
        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get_latest_req = connection_handler(self.session, req, self.server.verify_ssl)

        #RETURN NOTHING IF NO RESULTS
        if not get_latest_req:
            return

        influx_payload = []

        # Request Type: Movie = 1, TV Show = 0
        for result in get_latest_req['results']:
            if result['type'] == 'tv':
                req = self.session.prepare_request(Request('GET', self.server.url + tv_endpoint + str(result['media']['tmdbId'])))
                get_tv_req = connection_handler(self.session, req, self.server.verify_ssl)
                hash_id = hashit(f'{get_tv_req["id"]}{get_tv_req["name"]}')

                print(result)

                influx_payload.append(
                    {
                        "measurement": "Overseerr",
                        "tags": {
                            "type": "Requests",
                            "server": self.server.id,
                            "request_type": 0,
                            "status": get_tv_req['mediaInfo']['status'],
                            "title": get_tv_req['name'],
                            "requested_user": get_tv_req['mediaInfo']['requests'][0]['requestedBy']['plexUsername'],
                            "requested_date": get_tv_req['mediaInfo']['requests'][0]['requestedBy']['createdAt']
                        },
                        "time": now,
                        "fields": {
                            "hash": hash_id
                        }
                    }
                )

            if result['type'] == 'movie':
                req = self.session.prepare_request(Request('GET', self.server.url + movie_endpoint + str(result['media']['tmdbId'])))
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
                            "requested_user": get_movie_req['mediaInfo']['requests'][0]['requestedBy']['plexUsername'],
                            "requested_date": get_movie_req['mediaInfo']['requests'][0]['requestedBy']['createdAt']
                        },
                        "time": now,
                        "fields": {
                            "hash": hash_id
                        }
                    }
                )

        self.dbmanager.write_points(influx_payload)