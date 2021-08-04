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
        endpoint = '/api/v1/request?take=' + self.server.overseerr_num_latest_requests_to_fetch + '&filter=all&sort=added'
        movie_endpoint = 'https://requests.redredbeard.com/api/v1/movie/'
        tv_endpoint = 'https://requests.redredbeard.com/api/v1/tv/'

        #GET THE LATEST REQUESTS
        req = self.session.prepare_request(Request('GET', self.server.url + endpoint))
        get_latest_req = connection_handler(self.session, req, self.server.verify_ssl)

        #RETURN NOTHING IF NO RESULTS
        if not get_latest_req:
            return

        #SPLIT REQUESTS INTO TV/MOVIE LISTS AS THEY USE 2 DIFFERENT ENDPOINTS TO RETRIEVE DATA
        tv_requests = []
        movie_requests = []

        for result in get_latest_req['results']:
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

        influx_payload = []

        for tv in tv_requests:
            req = self.session.prepare_request(Request('GET', self.server.url + endpoint + tv['media']['tmdbId']))
            get_tv_req = connection_handler(self.session, req, self.server.verify_ssl)

            print(get_tv_req)





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
