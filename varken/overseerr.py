from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone

from varken.helpers import connection_handler, hashit
#from varken.structures import OmbiRequestCounts, OmbiIssuesCounts, OmbiMovieRequest, OmbiTVRequest
from varken.structures import OverseerrRequest


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

    def get_requests(self):
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
                    "type": "Requests",
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

        # # Request Type: Movie = 1, TV Show = 0
        # for movie in movie_requests:
        #     hash_id = hashit(f'{movie.id}{movie.theMovieDbId}{movie.title}')

        #     # Denied = 0, Approved = 1, Completed = 2, Pending = 3
        #     if movie.denied:
        #         status = 0

        #     elif movie.approved and movie.available:
        #         status = 2

        #     elif movie.approved:
        #         status = 1

        #     else:
        #         status = 3

        #     influx_payload.append(
        #         {
        #             "measurement": "Ombi",
        #             "tags": {
        #                 "type": "Requests",
        #                 "server": self.server.id,
        #                 "request_type": 1,
        #                 "status": status,
        #                 "title": movie.title,
        #                 "requested_user": movie.requestedUser['userAlias'],
        #                 "requested_date": movie.requestedDate
        #             },
        #             "time": now,
        #             "fields": {
        #                 "hash": hash_id
        #             }
        #         }
        #     )

    #     for show in tv_show_requests:
    #         hash_id = hashit(f'{show.id}{show.tvDbId}{show.title}')

    #         # Denied = 0, Approved = 1, Completed = 2, Pending = 3
    #         if show.childRequests[0].get('denied'):
    #             status = 0

    #         elif show.childRequests[0].get('approved') and show.childRequests[0].get('available'):
    #             status = 2

    #         elif show.childRequests[0].get('approved'):
    #             status = 1

    #         else:
    #             status = 3

    #         influx_payload.append(
    #             {
    #                 "measurement": "Ombi",
    #                 "tags": {
    #                     "type": "Requests",
    #                     "server": self.server.id,
    #                     "request_type": 0,
    #                     "status": status,
    #                     "title": show.title,
    #                     "requested_user": show.childRequests[0]['requestedUser']['userAlias'],
    #                     "requested_date": show.childRequests[0]['requestedDate']
    #                 },
    #                 "time": now,
    #                 "fields": {
    #                     "hash": hash_id
    #                 }
    #             }
    #         )

        if influx_payload:
            self.dbmanager.write_points(influx_payload)
        else:
            self.logger.debug("Empty dataset for overseerr module. Discarding...")

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
                    "available": requests.available
                }
            }
        ]

        self.dbmanager.write_points(influx_payload)

    # def get_issue_counts(self):
    #     now = datetime.now(timezone.utc).astimezone().isoformat()
    #     endpoint = '/api/v1/Issues/count'

    #     req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
    #     get = connection_handler(self.session, req, self.server.verify_ssl)

    #     if not get:
    #         return

    #     requests = OmbiIssuesCounts(**get)
    #     influx_payload = [
    #         {
    #             "measurement": "Ombi",
    #             "tags": {
    #                 "type": "Issues_Counts"
    #             },
    #             "time": now,
    #             "fields": {
    #                 "pending": requests.pending,
    #                 "in_progress": requests.inProgress,
    #                 "resolved": requests.resolved
    #             }
    #         }
    #     ]

    #     self.dbmanager.write_points(influx_payload)
