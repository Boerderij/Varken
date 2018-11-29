import sys
import configparser

from Varken.helpers import Server, TautulliServer, InfluxServer


class INIParser(object):
    def __init__(self):
        self.config = configparser.ConfigParser()

        self.influx_server = InfluxServer()
        self.sonarr_enabled = False
        self.sonarr_servers = []
        self.radarr_enabled = False
        self.radarr_servers = []
        self.ombi_enabled = False
        self.ombi_server = None
        self.tautulli_enabled = False
        self.tautulli_server = None
        self.asa_enabled = False
        self.asa = None
        self.read_file()
        self.parse_opts()

    def read_file(self):
        with open('varken.ini') as config_ini:
            self.config.read_file(config_ini)

    def parse_opts(self):
        # Parse InfluxDB options
        url = self.config.get('influxdb', 'url')
        port = self.config.getint('influxdb', 'port')
        username = self.config.get('influxdb', 'username')
        password = self.config.get('influxdb', 'password')

        self.influx_server = InfluxServer(url, port, username, password)

        # Parse Sonarr options
        try:
            if not self.config.getboolean('global', 'sonarr_server_ids'):
                sys.exit('sonarr_server_ids must be either false, or a comma-separated list of server ids')
        except ValueError:
            self.sonarr_enabled = True
            sids = self.config.get('global', 'sonarr_server_ids').strip(' ').split(',')

            for server_id in sids:
                sonarr_section = 'sonarr-' + server_id
                url = self.config.get(sonarr_section, 'url')
                apikey = self.config.get(sonarr_section, 'apikey')
                scheme = 'https://' if self.config.getboolean(sonarr_section, 'ssl') else 'http://'
                verify_ssl = self.config.getboolean(sonarr_section, 'verify_ssl')

                self.sonarr_servers.append(Server(server_id, scheme + url, apikey, verify_ssl))

        # Parse Radarr options
        try:
            if not self.config.getboolean('global', 'radarr_server_ids'):
                sys.exit('radarr_server_ids must be either false, or a comma-separated list of server ids')
        except ValueError:
            self.radarr_enabled = True
            sids = self.config.get('global', 'radarr_server_ids').strip(' ').split(',')
            for server_id in sids:
                radarr_section = 'sonarr-' + server_id
                url = self.config.get(radarr_section, 'url')
                apikey = self.config.get(radarr_section, 'apikey')
                scheme = 'https://' if self.config.getboolean(radarr_section, 'ssl') else 'http://'
                verify_ssl = self.config.getboolean(radarr_section, 'verify_ssl')

                self.radarr_servers.append(Server(server_id, scheme + url, apikey, verify_ssl))

        # Parse Tautulli options
        if self.config.getboolean('global', 'tautulli'):
            self.tautulli_enabled = True
            url = self.config.get('tautulli', 'url')
            fallback_ip = self.config.get('tautulli', 'fallback_ip')
            apikey = self.config.get('tautulli', 'apikey')
            scheme = 'https://' if self.config.getboolean('tautulli', 'ssl') else 'http://'
            verify_ssl = self.config.getboolean('tautulli', 'verify_ssl')
            db_name = self.config.get('tautulli', 'influx_db')

            self.tautulli_server = TautulliServer(scheme + url, fallback_ip, apikey, verify_ssl, db_name)

        # Parse Ombi Options
        if self.config.getboolean('global', 'ombi'):
            self.ombi_enabled = True
            url = self.config.get('ombi', 'url')
            apikey = self.config.get('ombi', 'apikey')
            scheme = 'https://' if self.config.getboolean('ombi', 'ssl') else 'http://'
            verify_ssl = self.config.getboolean('ombi', 'verify_ssl')

            self.ombi_server = Server(url=scheme + url, api_key=apikey, verify_ssl=verify_ssl)

        # Parse ASA opts
        if self.config.getboolean('global', 'asa'):
            self.asa_enabled = True
            url = self.config.get('asa', 'url')
            username = self.config.get('asa', 'username')
            password = self.config.get('asa', 'password')
            scheme = 'https://' if self.config.getboolean('asa', 'ssl') else 'http://'
            verify_ssl = self.config.getboolean('asa', 'verify_ssl')
            db_name = self.config.get('asa', 'influx_db')

            self.asa = (scheme + url, username, password, verify_ssl, db_name)
