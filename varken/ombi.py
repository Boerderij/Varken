from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.helpers import connection_handler, hashit
from varken.structures import OmbiRequestCounts, OmbiIssuesCounts, OmbiMovieRequest, OmbiTVRequest


class OmbiAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'Apikey': self.server.api_key}
        self.logger = getLogger()

    def __repr__(self):
        return f"<ombi-{self.server.id}>"

    def get_all_requests(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        tv_endpoint = '/api/v1/Request/tv'
        movie_endpoint = "/api/v1/Request/movie"

        tv_req = self.session.prepare_request(Request('GET', self.server.url + tv_endpoint))
        movie_req = self.session.prepare_request(Request('GET', self.server.url + movie_endpoint))
        get_tv = connection_handler(self.session, tv_req, self.server.verify_ssl) or []
        get_movie = connection_handler(self.session, movie_req, self.server.verify_ssl) or []

        if not any([get_tv, get_movie]):
            self.logger.error('No json replies. Discarding job')
            return

        if get_movie:
            movie_request_count = len(get_movie)
        else:
            movie_request_count = 0

        if get_tv:
            tv_request_count = len(get_tv)
        else:
            tv_request_count = 0

        tv_show_requests = []
        for show in get_tv:
            try:
                tv_show_requests.append(OmbiTVRequest(**show))
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating OmbiTVRequest structure for show. '
                                  'data attempted is: %s', e, show)

        movie_requests = []
        for movie in get_movie:
            try:
                movie_requests.append(OmbiMovieRequest(**movie))
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating OmbiMovieRequest structure for movie. '
                                  'data attempted is: %s', e, movie)

        influx_payload = [
            {
                "measurement": "Ombi",
                "tags": {
                    "type": "Request_Total",
                    "server": self.server.id
                },
                "time": now,
                "fields": {
                    "total": movie_request_count + tv_request_count,
                    "movies": movie_request_count,
                    "tv_shows": tv_request_count
                }
            }
        ]
        # Request Type: Movie = 1, TV Show = 0
        for movie in movie_requests:
            hash_id = hashit(f'{movie.id}{movie.theMovieDbId}{movie.title}')

            # Denied = 0, Approved = 1, Completed = 2, Pending = 3
            if movie.denied:
                status = 0

            elif movie.approved and movie.available:
                status = 2

            elif movie.approved:
                status = 1

            else:
                status = 3

            influx_payload.append(
                {
                    "measurement": "Ombi",
                    "tags": {
                        "type": "Requests",
                        "server": self.server.id,
                        "request_type": 1,
                        "status": status,
                        "title": movie.title,
                        "requested_user": movie.requestedUser['userAlias'],
                        "requested_date": movie.requestedDate
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        for show in tv_show_requests:
            hash_id = hashit(f'{show.id}{show.tvDbId}{show.title}')

            # Denied = 0, Approved = 1, Completed = 2, Pending = 3
            if show.childRequests[0].get('denied'):
                status = 0

            elif show.childRequests[0].get('approved') and show.childRequests[0].get('available'):
                status = 2

            elif show.childRequests[0].get('approved'):
                status = 1

            else:
                status = 3

            influx_payload.append(
                {
                    "measurement": "Ombi",
                    "tags": {
                        "type": "Requests",
                        "server": self.server.id,
                        "request_type": 0,
                        "status": status,
                        "title": show.title,
                        "requested_user": show.childRequests[0]['requestedUser']['userAlias'],
                        "requested_date": show.childRequests[0]['requestedDate']
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
            self.logger.debug("Empty dataset for ombi module. Discarding...")

    def get_request_counts(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
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
                "time": now,
                "fields": {
                    "pending": requests.pending,
                    "approved": requests.approved,
                    "available": requests.available
                }
            }
        ]

        self.dbmanager.write_points(influx_payload)

    def get_issue_counts(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        endpoint = '/api/v1/Issues/count'

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        requests = OmbiIssuesCounts(**get)
        influx_payload = [
            {
                "measurement": "Ombi",
                "tags": {
                    "type": "Issues_Counts"
                },
                "time": now,
                "fields": {
                    "pending": requests.pending,
                    "in_progress": requests.inProgress,
                    "resolved": requests.resolved
                }
            }
        ]

        self.dbmanager.write_points(influx_payload)
