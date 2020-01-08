from sys import exit
from logging import getLogger
from influxdb import InfluxDBClient
from requests.exceptions import ConnectionError
from influxdb.exceptions import InfluxDBServerError
from prometheus_client import start_http_server, Counter, Gauge


class DataManager(object):
    def __init__(self, config):
        self.config = config
        self.logger = getLogger()
        self.type = None
        self.prometheus = None
        self.influx = None
        if type(self.config).__name__ == "PrometheusClient":
            self.type = 'prometheus'
            self.prometheus = PrometheusExporter(self.config)
        else:
            self.type = 'influxdb'
            self.influx = InfluxClient(config)

    def update(self, data_type, data):
        json_data = data
        if self.influx:
            self.influx.write_points(data)
        elif self.prometheus:
            self.prometheus.parse_data(data)
        else:
            self.logger.error("Wtf... let a dev know a wtf happened...")


class InfluxClient(object):
    def __init__(self, server):
        self.server = server
        self.logger = getLogger()
        if self.server.url == "influxdb.domain.tld":
            self.logger.critical("You have not configured your varken.ini. Please read Wiki page for configuration")
            exit()
        self.influx = InfluxDBClient(host=self.server.url, port=self.server.port, username=self.server.username,
                                     password=self.server.password, ssl=self.server.ssl, database='varken',
                                     verify_ssl=self.server.verify_ssl)
        try:
            version = self.influx.request('ping', expected_response_code=204).headers['X-Influxdb-Version']
            self.logger.info('Influxdb version: %s', version)
        except ConnectionError:
            self.logger.critical("Error testing connection to InfluxDB. Please check your url/hostname")
            exit()

        databases = [db['name'] for db in self.influx.get_list_database()]

        if 'varken' not in databases:
            self.logger.info("Creating varken database")
            self.influx.create_database('varken')

            retention_policies = [policy['name'] for policy in
                                  self.influx.get_list_retention_policies(database='varken')]
            if 'varken 30d-1h' not in retention_policies:
                self.logger.info("Creating varken retention policy (30d-1h)")
                self.influx.create_retention_policy(name='varken 30d-1h', duration='30d', replication='1',
                                                    database='varken', default=True, shard_duration='1h')

    def write_points(self, data):
        d = data
        self.logger.debug('Writing Data to InfluxDB %s', d)
        try:
            self.influx.write_points(d)
        except (InfluxDBServerError, ConnectionError) as e:
            self.logger.error('Error writing data to influxdb. Dropping this set of data. '
                              'Check your database! Error: %s', e)


class PrometheusExporter(object):
    def __init__(self, config):
        self.config = config
        self.http_server = start_http_server(self.config.port, addr=self.config.url)
        self.logger = getLogger()

    def parse_data(self, data):
        json_data = data
        for d in json_data:
            app = d['measurement'].lower()
            prefix = f'varken_{app}'
            if app == 'unifi':
                for k, v in d.get('fields'):
                    field = f'{prefix}_{k}'
                    tags = d.get('tags')
                    attr = getattr(self, field)
                    if not attr:
                        n = Gauge(field, field, labelnames=tuple(tags.keys()), labelvalues=tuple(tags.values()))
                        setattr(self, field, n)
                        attr = getattr(self, field)
                    attr.set(v)
            elif app == 'ombi':






