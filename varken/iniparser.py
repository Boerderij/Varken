import configparser
import logging
from sys import exit
from os.path import join, exists
from varken.structures import SonarrServer, RadarrServer, OmbiServer, TautulliServer, InfluxServer, CiscoASAFirewall

logger = logging.getLogger()


class INIParser(object):
    def __init__(self, data_folder):
        self.config = configparser.ConfigParser(interpolation=None)
        self.data_folder = data_folder

        self.influx_server = InfluxServer()

        self.sonarr_enabled = False
        self.sonarr_servers = []

        self.radarr_enabled = False
        self.radarr_servers = []

        self.ombi_enabled = False
        self.ombi_servers = []

        self.tautulli_enabled = False
        self.tautulli_servers = []

        self.ciscoasa_enabled = False
        self.ciscoasa_firewalls = []

        try:
            self.parse_opts()
        except configparser.NoOptionError as e:
            logger.error(e)

    def enable_check(self, server_type=None):
        t = server_type
        global_server_ids = self.config.get('global', t)
        if global_server_ids.lower() in ['false', 'no', '0']:
            logger.info('%s disabled.', t.upper())
            return False
        else:
            sids = self.clean_check(global_server_ids, t)
            return sids

    @staticmethod
    def clean_check(server_id_list, server_type=None):
        t = server_type
        sid_list = server_id_list
        cleaned_list = sid_list.replace(' ', '').split(',')
        valid_sids = []
        for sid in cleaned_list:
            try:
                valid_sids.append(int(sid))
            except ValueError:
                logger.error("{} is not a valid server id number".format(sid))

        if valid_sids:
            logger.info('%s : %s', t.upper(), valid_sids)
            return valid_sids
        else:
            logger.error('No valid %s', t.upper())
            return False

    def read_file(self):
        file_path = join(self.data_folder, 'varken.ini')
        if exists(file_path):
            with open(file_path) as config_ini:
                self.config.read_file(config_ini)
        else:
            exit('Config file missing (varken.ini) in {}'.format(self.data_folder))

    def parse_opts(self):
        self.read_file()
        # Parse InfluxDB options
        url = self.config.get('influxdb', 'url')
        port = self.config.getint('influxdb', 'port')
        username = self.config.get('influxdb', 'username')
        password = self.config.get('influxdb', 'password')

        self.influx_server = InfluxServer(url, port, username, password)

        # Parse Sonarr options
        self.sonarr_enabled = self.enable_check('sonarr_server_ids')

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
        self.radarr_enabled = self.enable_check('radarr_server_ids')

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
        self.tautulli_enabled = self.enable_check('tautulli_server_ids')

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

                server = TautulliServer(server_id, scheme + url, fallback_ip, apikey, verify_ssl, get_activity,
                                        get_activity_run_seconds)
                self.tautulli_servers.append(server)

        # Parse Ombi options
        self.ombi_enabled = self.enable_check('ombi_server_ids')

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
        self.ciscoasa_enabled = self.enable_check('ciscoasa_firewall_ids')

        if self.ciscoasa_enabled:
            fids = self.config.get('global', 'ciscoasa_firewall_ids').strip(' ').split(',')
            for firewall_id in fids:
                ciscoasa_section = 'ciscoasa-' + firewall_id
                url = self.config.get(ciscoasa_section, 'url')
                username = self.config.get(ciscoasa_section, 'username')
                password = self.config.get(ciscoasa_section, 'password')
                scheme = 'https://' if self.config.getboolean(ciscoasa_section, 'ssl') else 'http://'
                verify_ssl = self.config.getboolean(ciscoasa_section, 'verify_ssl')
                if scheme != 'https://':
                    verify_ssl = False
                outside_interface = self.config.get(ciscoasa_section, 'outside_interface')
                get_bandwidth_run_seconds = self.config.getint(ciscoasa_section, 'get_bandwidth_run_seconds')

                firewall = CiscoASAFirewall(firewall_id, scheme + url, username, password, outside_interface,
                                            verify_ssl, get_bandwidth_run_seconds)
                self.ciscoasa_firewalls.append(firewall)
