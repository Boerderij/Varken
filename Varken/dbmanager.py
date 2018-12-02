from influxdb import InfluxDBClient

class DBManager(object):
    def __init__(self, server):
        self.server = server
        self.influx = InfluxDBClient(self.server.url, self.server.port, self.server.username, self.server.password,
                                     'varken')
        databases = [db['name'] for db in self.influx.get_list_database()]

        if 'varken' not in databases:
            self.influx.create_database('varken')
            self.influx.create_retention_policy('Varken 30d/1h', '30d', '1', 'varken', False, '1h')

    def write_points(self, data):
        self.influx.write_points(data)