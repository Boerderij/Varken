import sys
import configparser
from os.path import abspath, dirname, join
from Varken.helpers import OmbiServer, TautulliServer, SonarrServer, InfluxServer, RadarrServer


class INIParser(object):
    def __init__(self):
        self.config = configparser.ConfigParser()

        self.influx_server = InfluxServer()

        self.sonarr_enabled = False
        self.sonarr_servers = []

        self.radarr_enabled = False
        self.radarr_servers = []

        self.ombi_enabled = False
        self.ombi_servers = []

        self.tautulli_enabled = False
        self.tautulli_servers = []

        self.asa_enabled = False
        self.asa = None

        self.parse_opts()

    def read_file(self):
        file_path = abspath(join(dirname(__file__), '..', 'data', 'varken.ini'))
        with open(file_path) as config_ini:
            self.config.read_file(config_ini)

    def parse_opts(self):
        self.read_file()
        # Parse InfluxDB options
        url = self.config.get('influxdb', 'url')
        port = self.config.getint('influxdb', 'port')
        username = self.config.get('influxdb', 'username')
        password = self.config.get('influxdb', 'password')

        self.influx_server = InfluxServer(url, port, username, password)

        # Parse Sonarr options
        try:
            if not self.config.getboolean('global', 'sonarr_server_ids'):
                sys.exit('server_ids must be either false, or a comma-separated list of server ids')
            elif self.config.getint('global', 'sonarr_server_ids'):
                self.sonarr_enabled = True
        except ValueError:
            self.sonarr_enabled = True

        if self.sonarr_enabled:
            sids = self.config.get('global', 'sonarr_server_ids').strip(' ').split(',')

            for server_id in sids:
                sonarr_section = 'sonarr-' + server_id
                url = self.config.get(sonarr_section, 'url')
                apikey = self.config.get(sonarr_section, 'apikey')
                scheme = 'https://' if self.config.getboolean(sonarr_section, 'ssl') else 'http://'
                verify_ssl = self.config.getboolean(sonarr_section, 'verify_ssl')
                if scheme != 'https://':
                    verify_ssl = False
                queue = self.config.getboolean(sonarr_section, 'queue')
                missing_days = self.config.getint(sonarr_section, 'missing_days')
                future_days = self.config.getint(sonarr_section, 'future_days')
                missing_days_run_seconds = self.config.getint(sonarr_section, 'missing_days_run_seconds')
                future_days_run_seconds = self.config.getint(sonarr_section, 'future_days_run_seconds')
                queue_run_seconds = self.config.getint(sonarr_section, 'queue_run_seconds')

                server = SonarrServer(server_id, scheme + url, apikey, verify_ssl, missing_days,
                                      missing_days_run_seconds, future_days, future_days_run_seconds,
                                      queue, queue_run_seconds)
                self.sonarr_servers.append(server)

        # Parse Radarr options
        try:
            if not self.config.getboolean('global', 'radarr_server_ids'):
                sys.exit('server_ids must be either false, or a comma-separated list of server ids')
            elif self.config.getint('global', 'radarr_server_ids'):
                self.radarr_enabled = True
        except ValueError:
            self.radarr_enabled = True

        if self.radarr_enabled:
            sids = self.config.get('global', 'radarr_server_ids').strip(' ').split(',')

            for server_id in sids:
                radarr_section = 'radarr-' + server_id
                url = self.config.get(radarr_section, 'url')
                apikey = self.config.get(radarr_section, 'apikey')
                scheme = 'https://' if self.config.getboolean(radarr_section, 'ssl') else 'http://'
                verify_ssl = self.config.getboolean(radarr_section, 'verify_ssl')
                if scheme != 'https://':
                    verify_ssl = False
                queue = self.config.getboolean(radarr_section, 'queue')
                queue_run_seconds = self.config.getint(radarr_section, 'queue_run_seconds')
                get_missing = self.config.getboolean(radarr_section, 'get_missing')
                get_missing_run_seconds = self.config.getint(radarr_section, 'get_missing_run_seconds')

                server = RadarrServer(server_id, scheme + url, apikey, verify_ssl, queue, queue_run_seconds,
                                      get_missing, get_missing_run_seconds)
                self.radarr_servers.append(server)

        # Parse Tautulli options
        try:
            if not self.config.getboolean('global', 'tautulli_server_ids'):
                sys.exit('server_ids must be either false, or a comma-separated list of server ids')
            elif self.config.getint('global', 'tautulli_server_ids'):
                self.tautulli_enabled = True
        except ValueError:
            self.tautulli_enabled = True

        if self.tautulli_enabled:
            sids = self.config.get('global', 'tautulli_server_ids').strip(' ').split(',')

            for server_id in sids:
                tautulli_section = 'tautulli-' + server_id
                url = self.config.get(tautulli_section, 'url')
                fallback_ip = self.config.get(tautulli_section, 'fallback_ip')
                apikey = self.config.get(tautulli_section, 'apikey')
                scheme = 'https://' if self.config.getboolean(tautulli_section, 'ssl') else 'http://'
                verify_ssl = self.config.getboolean(tautulli_section, 'verify_ssl')
                if scheme != 'https://':
                    verify_ssl = False
                get_activity = self.config.getboolean(tautulli_section, 'get_activity')
                get_activity_run_seconds = self.config.getint(tautulli_section, 'get_activity_run_seconds')
                get_sessions = self.config.getboolean(tautulli_section, 'get_sessions')
                get_sessions_run_seconds = self.config.getint(tautulli_section, 'get_sessions_run_seconds')

                server = TautulliServer(server_id, scheme + url, fallback_ip, apikey, verify_ssl, get_activity,
                                        get_activity_run_seconds, get_sessions, get_sessions_run_seconds)
                self.tautulli_servers.append(server)

        # Parse Ombi Options
        try:
            if not self.config.getboolean('global', 'ombi_server_ids'):
                sys.exit('server_ids must be either false, or a comma-separated list of server ids')
            elif self.config.getint('global', 'ombi_server_ids'):
                self.ombi_enabled = True
        except ValueError:
            self.ombi_enabled = True

        if self.ombi_enabled:
            sids = self.config.get('global', 'ombi_server_ids').strip(' ').split(',')
            for server_id in sids:
                ombi_section = 'ombi-' + server_id
                url = self.config.get(ombi_section, 'url')
                apikey = self.config.get(ombi_section, 'apikey')
                scheme = 'https://' if self.config.getboolean(ombi_section, 'ssl') else 'http://'
                verify_ssl = self.config.getboolean(ombi_section, 'verify_ssl')
                if scheme != 'https://':
                    verify_ssl = False
                request_type_counts = self.config.getboolean(ombi_section, 'get_request_type_counts')
                request_type_run_seconds = self.config.getint(ombi_section, 'request_type_run_seconds')
                request_total_counts = self.config.getboolean(ombi_section, 'get_request_total_counts')
                request_total_run_seconds = self.config.getint(ombi_section, 'request_total_run_seconds')

                server = OmbiServer(server_id, scheme + url, apikey, verify_ssl, request_type_counts,
                                    request_type_run_seconds, request_total_counts, request_total_run_seconds)
                self.ombi_servers.append(server)

        # Parse ASA opts
        if self.config.getboolean('global', 'asa'):
            self.asa_enabled = True
            url = self.config.get('asa', 'url')
            username = self.config.get('asa', 'username')
            password = self.config.get('asa', 'password')
            scheme = 'https://' if self.config.getboolean('asa', 'ssl') else 'http://'
            verify_ssl = self.config.getboolean('asa', 'verify_ssl')
            if scheme != 'https://':
                verify_ssl = False
            db_name = self.config.get('asa', 'influx_db')

            self.asa = (scheme + url, username, password, verify_ssl, db_name)
