from sys import exit
from logging import getLogger
from requests.exceptions import ConnectionError
import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDB2Manager(object):
    def __init__(self, server):
        self.server = server
        self.logger = getLogger()
        if self.server.url == "influxdb2.domain.tld":
            self.logger.critical("You have not configured your varken.ini. Please read Wiki page for configuration")
            exit()

        self.influx = InfluxDBClient(url=self.server.url, token=self.server.token, org=self.server.org,
                                    timeout=self.server.timeout, verify_ssl=self.server.verify_ssl, ssl_ca_cert=self.server.ssl)
        self.influx_write_api = self.influx.write_api(write_options=SYNCHRONOUS)

        # Create the bucket if needed

        bucket_api = self.influx.buckets_api()

        bucket = bucket_api.find_bucket_by_name(self.server.bucket)

        if bucket is None:
            self.logger.info('Creating bucket %s', self.server.bucket)

            org_api = influxdb_client.service.organizations_service.OrganizationsService(self.influx.api_client)
            orgs = org_api.get_orgs()
            for org in orgs.orgs:
                if org.name == self.server.org:
                    my_org = org

            self.influx.buckets_api().create_bucket(bucket_name=self.server.bucket, org_id=my_org.id)

    def write_points(self, data):
        d = data
        self.logger.info('Writing Data to InfluxDBv2 %s', d)

        try:
            self.influx_write_api.write(bucket=self.server.bucket, record=d)
        except (InfluxDBServerError, ConnectionError) as e:
            self.logger.error('Error writing data to influxdb2. Dropping this set of data. '
                              'Check your database! Error: %s', e)
