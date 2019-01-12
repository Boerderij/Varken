from logging import getLogger
from influxdb import InfluxDBClient


class DBManager(object):
    def __init__(self, server):
        self.server = server
        self.influx = InfluxDBClient(host=self.server.url, port=self.server.port, username=self.server.username,
                                     password=self.server.password, ssl=self.server.ssl, database='varken',
                                     verify_ssl=self.server.verify_ssl)
        databases = [db['name'] for db in self.influx.get_list_database()]
        self.logger = getLogger()

        if 'varken' not in databases:
            self.logger.info("Creating varken database")
            self.influx.create_database('varken')

            self.logger.info("Creating varken retention policy (30d/1h)")
            self.influx.create_retention_policy('varken 30d/1h', '30d', '1', 'varken', False, '1h')

    def write_points(self, data):
        d = data
        self.logger.debug('Writing Data to InfluxDB %s', d)
        self.influx.write_points(d)
