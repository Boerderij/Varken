from logging import getLogger
from os.path import join, exists
from re import match, compile, IGNORECASE
from configparser import ConfigParser, NoOptionError

from varken.helpers import clean_sid_check
from varken.structures import SickChillServer
from varken.varkenlogger import BlacklistFilter
from varken.structures import SonarrServer, RadarrServer, OmbiServer, TautulliServer, InfluxServer, CiscoASAFirewall


class INIParser(object):
    def __init__(self, data_folder):
        self.config = ConfigParser(interpolation=None)
        self.data_folder = data_folder

        self.logger = getLogger()

        self.influx_server = InfluxServer()

        self.sonarr_enabled = False
        self.sonarr_servers = []

        self.radarr_enabled = False
        self.radarr_servers = []

        self.ombi_enabled = False
        self.ombi_servers = []

        self.tautulli_enabled = False
        self.tautulli_servers = []

        self.sickchill_enabled = False
        self.sickchill_servers = []

        self.ciscoasa_enabled = False
        self.ciscoasa_firewalls = []

        self.parse_opts()

        self.filtered_strings = None

    def config_blacklist(self):
        filtered_strings = [section.get(k) for key, section in self.config.items()
                            for k in section if k in BlacklistFilter.blacklisted_strings]
        self.filtered_strings = list(filter(None, filtered_strings))
        # Added matching for domains that use /locations. ConnectionPool ignores the location in logs
        domains_only = list([ string.split('/')[0] for string in filtered_strings if '/' in string ])
        self.filtered_strings.extend(domains_only)

        for handler in self.logger.handlers:
            handler.addFilter(BlacklistFilter(set(self.filtered_strings)))

    def enable_check(self, server_type=None):
        t = server_type
        try:
            global_server_ids = self.config.get('global', t)
            if global_server_ids.lower() in ['false', 'no', '0']:
                self.logger.info('%s disabled.', t.upper())
            else:
                sids = clean_sid_check(global_server_ids, t)
                return sids
        except NoOptionError as e:
            self.logger.error(e)

    def read_file(self):
        file_path = join(self.data_folder, 'varken.ini')
        if exists(file_path):
            with open(file_path) as config_ini:
                self.config.read_file(config_ini)
            self.config_blacklist()
        else:
            self.logger.error('Config file missing (varken.ini) in %s', self.data_folder)
            exit(1)

    def url_check(self, url=None, include_port=True):
        url_check = url
        inc_port = include_port

        search = (r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                  r'localhost|'  # localhost...
                  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                  )

        if inc_port:
            search = (search + r'(?::\d+)?' + r'(?:/?|[/?]\S+)$')
        else:
            search = (search + r'(?:/?|[/?]\S+)$')

        regex = compile('{}'.format(search), IGNORECASE)

        print(match(regex, url_check))

        valid = match(regex, url_check) is not None
        if not valid:
            if inc_port:
                self.logger.error('%s is invalid! URL must host/IP and port if not 80 or 443. ie. localhost:8080',
                                  url_check)
                exit(1)
            else:
                self.logger.error('%s is invalid! URL must host/IP. ie. localhost', url_check)
                exit(1)
        else:
            self.logger.debug('%s is a valid URL in the config.', url_check)
            return url_check

    def parse_opts(self):
        self.read_file()
        # Parse InfluxDB options
        url = self.url_check(self.config.get('influxdb', 'url'), include_port=False)

        port = self.config.getint('influxdb', 'port')

        username = self.config.get('influxdb', 'username')

        password = self.config.get('influxdb', 'password')

        self.influx_server = InfluxServer(url, port, username, password)

        # Parse Sonarr options
        self.sonarr_enabled = self.enable_check('sonarr_server_ids')

        if self.sonarr_enabled:
            for server_id in self.sonarr_enabled:
                section = 'sonarr-' + str(server_id)
                try:
                    url = self.url_check(self.config.get(section, 'url'))

                    apikey = self.config.get(section, 'apikey')

                    scheme = 'https://' if self.config.getboolean(section, 'ssl') else 'http://'

                    verify_ssl = self.config.getboolean(section, 'verify_ssl')

                    if scheme != 'https://':
                        verify_ssl = False

                    queue = self.config.getboolean(section, 'queue')

                    missing_days = self.config.getint(section, 'missing_days')

                    future_days = self.config.getint(section, 'future_days')

                    missing_days_run_seconds = self.config.getint(section, 'missing_days_run_seconds')

                    future_days_run_seconds = self.config.getint(section, 'future_days_run_seconds')

                    queue_run_seconds = self.config.getint(section, 'queue_run_seconds')

                    server = SonarrServer(server_id, scheme + url, apikey, verify_ssl, missing_days,
                                          missing_days_run_seconds, future_days, future_days_run_seconds,
                                          queue, queue_run_seconds)

                    self.sonarr_servers.append(server)
                except NoOptionError as e:
                    self.sonarr_enabled = False
                    self.logger.error(
                        '%s disabled. Error: %s', section, e)

        # Parse Radarr options
        self.radarr_enabled = self.enable_check('radarr_server_ids')

        if self.radarr_enabled:
            for server_id in self.radarr_enabled:
                section = 'radarr-' + str(server_id)
                try:
                    url = self.url_check(self.config.get(section, 'url'))

                    apikey = self.config.get(section, 'apikey')

                    scheme = 'https://' if self.config.getboolean(section, 'ssl') else 'http://'

                    verify_ssl = self.config.getboolean(section, 'verify_ssl')

                    if scheme != 'https://':
                        verify_ssl = False

                    queue = self.config.getboolean(section, 'queue')

                    queue_run_seconds = self.config.getint(section, 'queue_run_seconds')

                    get_missing = self.config.getboolean(section, 'get_missing')

                    get_missing_run_seconds = self.config.getint(section, 'get_missing_run_seconds')

                    server = RadarrServer(server_id, scheme + url, apikey, verify_ssl, queue, queue_run_seconds,
                                          get_missing, get_missing_run_seconds)
                    self.radarr_servers.append(server)
                except NoOptionError as e:
                    self.radarr_enabled = False
                    self.logger.error(
                        '%s disabled. Error: %s', section, e)

        # Parse Tautulli options
        self.tautulli_enabled = self.enable_check('tautulli_server_ids')

        if self.tautulli_enabled:
            for server_id in self.tautulli_enabled:
                section = 'tautulli-' + str(server_id)
                try:
                    url = self.url_check(self.config.get(section, 'url'))

                    fallback_ip = self.config.get(section, 'fallback_ip')

                    apikey = self.config.get(section, 'apikey')

                    scheme = 'https://' if self.config.getboolean(section, 'ssl') else 'http://'

                    verify_ssl = self.config.getboolean(section, 'verify_ssl')

                    if scheme != 'https://':
                        verify_ssl = False

                    get_activity = self.config.getboolean(section, 'get_activity')

                    get_activity_run_seconds = self.config.getint(section, 'get_activity_run_seconds')

                    server = TautulliServer(server_id, scheme + url, fallback_ip, apikey, verify_ssl, get_activity,
                                            get_activity_run_seconds)
                    self.tautulli_servers.append(server)
                except NoOptionError as e:
                    self.tautulli_enabled = False
                    self.logger.error(
                        '%s disabled. Error: %s', section, e)

        # Parse Ombi options
        self.ombi_enabled = self.enable_check('ombi_server_ids')

        if self.ombi_enabled:
            for server_id in self.ombi_enabled:
                section = 'ombi-' + str(server_id)
                try:
                    url = self.url_check(self.config.get(section, 'url'))

                    apikey = self.config.get(section, 'apikey')

                    scheme = 'https://' if self.config.getboolean(section, 'ssl') else 'http://'

                    verify_ssl = self.config.getboolean(section, 'verify_ssl')

                    if scheme != 'https://':
                        verify_ssl = False

                    request_type_counts = self.config.getboolean(section, 'get_request_type_counts')

                    request_type_run_seconds = self.config.getint(section, 'request_type_run_seconds')

                    request_total_counts = self.config.getboolean(section, 'get_request_total_counts')

                    request_total_run_seconds = self.config.getint(section, 'request_total_run_seconds')

                    server = OmbiServer(server_id, scheme + url, apikey, verify_ssl, request_type_counts,
                                        request_type_run_seconds, request_total_counts, request_total_run_seconds)
                    self.ombi_servers.append(server)
                except NoOptionError as e:
                    self.ombi_enabled = False
                    self.logger.error(
                        '%s disabled. Error: %s', section, e)

        # Parse SickChill options
        self.sickchill_enabled = self.enable_check('sickchill_server_ids')

        if self.sickchill_enabled:
            for server_id in self.sickchill_enabled:
                section = 'sickchill-' + str(server_id)
                try:
                    url = self.url_check(self.config.get(section, 'url'))

                    apikey = self.config.get(section, 'apikey')

                    scheme = 'https://' if self.config.getboolean(section, 'ssl') else 'http://'

                    verify_ssl = self.config.getboolean(section, 'verify_ssl')

                    if scheme != 'https://':
                        verify_ssl = False

                    get_missing = self.config.getboolean(section, 'get_missing')

                    get_missing_run_seconds = self.config.getint(section, 'get_missing_run_seconds')

                    server = SickChillServer(server_id, scheme + url, apikey, verify_ssl,
                                             get_missing, get_missing_run_seconds)
                    self.sickchill_servers.append(server)
                except NoOptionError as e:
                    self.sickchill_enabled = False
                    self.logger.error(
                        '%s disabled. Error: %s', section, e)

        # Parse ASA opts
        self.ciscoasa_enabled = self.enable_check('ciscoasa_firewall_ids')

        if self.ciscoasa_enabled:
            for firewall_id in self.ciscoasa_enabled:
                section = 'ciscoasa-' + str(firewall_id)
                try:
                    url = self.url_check(self.config.get(section, 'url'))

                    username = self.config.get(section, 'username')

                    password = self.config.get(section, 'password')

                    scheme = 'https://' if self.config.getboolean(section, 'ssl') else 'http://'

                    verify_ssl = self.config.getboolean(section, 'verify_ssl')

                    if scheme != 'https://':
                        verify_ssl = False

                    outside_interface = self.config.get(section, 'outside_interface')

                    get_bandwidth_run_seconds = self.config.getint(section, 'get_bandwidth_run_seconds')

                    firewall = CiscoASAFirewall(firewall_id, scheme + url, username, password, outside_interface,
                                                verify_ssl, get_bandwidth_run_seconds)
                    self.ciscoasa_firewalls.append(firewall)
                except NoOptionError as e:
                    self.ciscoasa_enabled = False
                    self.logger.error(
                        '%s disabled. Error: %s', section, e)
