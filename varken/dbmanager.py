import re
from sys import exit
from logging import getLogger
from influxdb_client import InfluxDBClient, BucketRetentionRules
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
from urllib3.exceptions import NewConnectionError


class DBManager(object):
    def __init__(self, server):
        self.server = server
        self.logger = getLogger()
        self.bucket = "varken"

        if self.server.url == "influxdb.domain.tld":
            self.logger.critical("You have not configured your varken.ini. Please read Wiki page for configuration")
            exit()

        url = self.server.url
        if 'http' not in url:
            scheme = 'http'
            if self.server.ssl:
                scheme = 'https'
            url = "{}://{}:{}".format(scheme, self.server.url, self.server.port)
        token = f'{self.server.username}:{self.server.password}'

        self.influx = InfluxDBClient(url=url, token=token,
                                     verify_ssl=self.server.verify_ssl, org=self.server.org)

        try:
            version = self.influx.version()
            self.logger.info('Influxdb version: %s', version)
            match = re.match(r'v?(\d+)\.', version)
            if match:
                self.version = int(match[1])
                self.logger.info("Using InfluxDB API v%s", self.version)
            else:
                self.logger.critical("Unknown influxdb version")
                exit(1)
        except NewConnectionError:
            self.logger.critical("Error getting InfluxDB version number. Please check your url/hostname are valid")
            exit(1)

        if self.version >= 2:
            # If we pass username/password to a v1 server, it breaks :(
            self.influx = InfluxDBClient(url=url, username=self.server.username,
                                         password=self.server.password,
                                         verify_ssl=self.server.verify_ssl, org=self.server.org)
            self.create_v2_bucket()
        else:
            self.create_v1_database()

    def create_v2_bucket(self):
        if not self.influx.buckets_api().find_bucket_by_name(self.bucket):
            self.logger.info("Creating varken bucket")

            retention = BucketRetentionRules(type="expire", every_seconds=60 * 60 * 24 * 30,
                                             shard_group_duration_seconds=60 * 60)
            self.influx.buckets_api().create_bucket(bucket_name=self.bucket,
                                                    retention_rules=retention)

    def create_v1_database(self):
        from influxdb import InfluxDBClient
        client = InfluxDBClient(host=self.server.url, port=self.server.port, username=self.server.username,
                                password=self.server.password, ssl=self.server.ssl, database=self.bucket,
                                verify_ssl=self.server.verify_ssl)
        databases = [db['name'] for db in client.get_list_database()]

        if self.bucket not in databases:
            self.logger.info("Creating varken database")
            client.create_database(self.bucket)

            retention_policies = [policy['name'] for policy in
                                  client.get_list_retention_policies(database=self.bucket)]
            if 'varken 30d-1h' not in retention_policies:
                self.logger.info("Creating varken retention policy (30d-1h)")
                client.create_retention_policy(name='varken 30d-1h', duration='30d', replication='1',
                                               database=self.bucket, default=True, shard_duration='1h')

        self.bucket = f'{self.bucket}/varken 30d-1h'

    def write_points(self, data):
        d = data
        self.logger.debug('Writing Data to InfluxDB %s', d)
        write_api = self.influx.write_api(write_options=SYNCHRONOUS)
        try:
            write_api.write(bucket=self.bucket, record=data)
        except (InfluxDBError, NewConnectionError) as e:
            self.logger.error('Error writing data to influxdb. Dropping this set of data. '
                              'Check your database! Error: %s', e)
