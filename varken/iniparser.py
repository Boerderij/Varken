from shutil import copyfile
from logging import getLogger
from os.path import join, exists
from re import match, compile, IGNORECASE
from configparser import ConfigParser, NoOptionError, NoSectionError

from varken.varkenlogger import BlacklistFilter
from varken.structures import SickChillServer, UniFiServer
from varken.helpers import clean_sid_check, rfc1918_ip_check
from varken.structures import SonarrServer, RadarrServer, OmbiServer, TautulliServer, InfluxServer


class INIParser(object):
    def __init__(self, data_folder):
        self.config = None
        self.data_folder = data_folder
        self.filtered_strings = None
        self.services = ['sonarr', 'radarr', 'lidarr', 'ombi', 'tautulli', 'sickchill', 'unifi']

        self.logger = getLogger()
        self.influx_server = InfluxServer()

        try:
            self.parse_opts(read_file=True)
        except NoSectionError as e:
            self.logger.error('Missing section in (varken.ini): %s', e)
            self.rectify_ini()

    def config_blacklist(self):
        filtered_strings = [section.get(k) for key, section in self.config.items()
                            for k in section if k in BlacklistFilter.blacklisted_strings]
        self.filtered_strings = list(filter(None, filtered_strings))
        # Added matching for domains that use /locations. ConnectionPool ignores the location in logs
        domains_only = [string.split('/')[0] for string in filtered_strings if '/' in string]
        self.filtered_strings.extend(domains_only)
        # Added matching for domains that use :port. ConnectionPool splits the domain/ip from the port
        without_port = [string.split(':')[0] for string in filtered_strings if ':' in string]
        self.filtered_strings.extend(without_port)

        for handler in self.logger.handlers:
            handler.addFilter(BlacklistFilter(set(self.filtered_strings)))

    def enable_check(self, server_type=None):
        t = server_type
        global_server_ids = self.config.get('global', t)
        if global_server_ids.lower() in ['false', 'no', '0']:
            self.logger.info('%s disabled.', t.upper())
        else:
            sids = clean_sid_check(global_server_ids, t)
            return sids

    def read_file(self, inifile):
        config = ConfigParser(interpolation=None)
        ini = inifile
        file_path = join(self.data_folder, ini)

        if not exists(file_path):
            self.logger.error('File missing (%s) in %s', ini, self.data_folder)
            if inifile == 'varken.ini':
                try:
                    self.logger.debug('Creating varken.ini from varken.example.ini')
                    copyfile(join(self.data_folder, 'varken.example.ini'), file_path)
                except IOError as e:
                    self.logger.error("Varken does not have permission to write to %s. Error: %s - Exiting.", e,
                                      self.data_folder)
                    exit(1)

        self.logger.debug('Reading from %s', inifile)
        with open(file_path) as config_ini:
            config.read_file(config_ini)

        return config

    def write_file(self, inifile):
        ini = inifile
        file_path = join(self.data_folder, ini)
        if exists(file_path):
            self.logger.debug('Writing to %s', inifile)
            with open(file_path, 'w') as config_ini:
                self.config.write(config_ini)
        else:
            self.logger.error('File missing (%s) in %s', ini, self.data_folder)
            exit(1)

    def url_check(self, url=None, include_port=True, section=None):
        url_check = url
        module = section
        inc_port = include_port

        search = (r'(?:([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}|'  # domain...
                  r'localhost|'  # localhost...
                  r'^[a-zA-Z0-9_-]*|'  # hostname only. My soul dies a little every time this is used...
                  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                  )
        # Include search for port if it is needed.
        if inc_port:
            search = (search + r'(?::\d+)?' + r'(?:/?|[/?]\S+)$')
        else:
            search = (search + r'(?:/?|[/?]\S+)$')

        regex = compile('{}'.format(search), IGNORECASE)

        valid = match(regex, url_check) is not None
        if not valid:
            if inc_port:
                self.logger.error('%s is invalid in module [%s]! URL must host/IP and '
                                  'port if not 80 or 443. ie. localhost:8080',
                                  url_check, module)
                exit(1)
            else:
                self.logger.error('%s is invalid in module [%s]! URL must host/IP. ie. localhost', url_check, module)
                exit(1)
        else:
            self.logger.debug('%s is a valid URL in module [%s].', url_check, module)
            return url_check

    def rectify_ini(self):
        self.logger.debug('Rectifying varken.ini with varken.example.ini')
        current_ini = self.config
        example_ini = self.read_file('varken.example.ini')

        for name, section in example_ini.items():
            if name not in current_ini:
                self.logger.debug('Section %s missing. Adding...', name)
                current_ini[name] = {}
            for key, value in section.items():
                if not current_ini[name].get(key):
                    self.logger.debug('%s is missing in %s. Adding defaults...', key, name)
                    current_ini[name][key] = value

        self.config = current_ini
        self.write_file('varken.ini')
        self.parse_opts()

    def parse_opts(self, read_file=False):
        for service in self.services:
            setattr(self, f'{service}_servers', [])

        if read_file:
            self.config = self.read_file('varken.ini')
            self.config_blacklist()
        # Parse InfluxDB options
        try:
            url = self.url_check(self.config.get('influxdb', 'url'), include_port=False, section='influxdb')
            port = self.config.getint('influxdb', 'port')
            ssl = self.config.getboolean('influxdb', 'ssl')
            verify_ssl = self.config.getboolean('influxdb', 'verify_ssl')

            username = self.config.get('influxdb', 'username')
            password = self.config.get('influxdb', 'password')
        except NoOptionError as e:
            self.logger.error('Missing key in %s. Error: %s', "influxdb", e)
            self.rectify_ini()
            return

        self.influx_server = InfluxServer(url=url, port=port, username=username, password=password, ssl=ssl,
                                          verify_ssl=verify_ssl)

        # Check for all enabled services
        for service in self.services:
            try:
                setattr(self, f'{service}_enabled', self.enable_check(f'{service}_server_ids'))
            except NoOptionError as e:
                self.logger.error('Missing global %s. Error: %s', f'{service}_server_ids', e)
                self.rectify_ini()
                return
            service_enabled = getattr(self, f'{service}_enabled')

            if service_enabled:
                for server_id in service_enabled:
                    server = None
                    section = f"{service}-{server_id}"
                    try:
                        url = self.url_check(self.config.get(section, 'url'), section=section)

                        apikey = None
                        if service != 'unifi':
                            apikey = self.config.get(section, 'apikey')

                        scheme = 'https://' if self.config.getboolean(section, 'ssl') else 'http://'
                        verify_ssl = self.config.getboolean(section, 'verify_ssl')

                        if scheme != 'https://':
                            verify_ssl = False

                        if service in ['sonarr', 'radarr', 'lidarr']:
                            queue = self.config.getboolean(section, 'queue')
                            queue_run_seconds = self.config.getint(section, 'queue_run_seconds')

                        if service in ['sonarr', 'lidarr']:
                            missing_days = self.config.getint(section, 'missing_days')
                            future_days = self.config.getint(section, 'future_days')

                            missing_days_run_seconds = self.config.getint(section, 'missing_days_run_seconds')
                            future_days_run_seconds = self.config.getint(section, 'future_days_run_seconds')

                            server = SonarrServer(id=server_id, url=scheme + url, api_key=apikey, verify_ssl=verify_ssl,
                                                  missing_days=missing_days, future_days=future_days,
                                                  missing_days_run_seconds=missing_days_run_seconds,
                                                  future_days_run_seconds=future_days_run_seconds,
                                                  queue=queue, queue_run_seconds=queue_run_seconds)

                        if service == 'radarr':
                            get_missing = self.config.getboolean(section, 'get_missing')
                            get_missing_run_seconds = self.config.getint(section, 'get_missing_run_seconds')

                            server = RadarrServer(id=server_id, url=scheme + url, api_key=apikey, verify_ssl=verify_ssl,
                                                  queue_run_seconds=queue_run_seconds, get_missing=get_missing,
                                                  queue=queue, get_missing_run_seconds=get_missing_run_seconds)

                        if service == 'tautulli':
                            fallback_ip = self.config.get(section, 'fallback_ip')

                            get_stats = self.config.getboolean(section, 'get_stats')
                            get_activity = self.config.getboolean(section, 'get_activity')

                            get_activity_run_seconds = self.config.getint(section, 'get_activity_run_seconds')
                            get_stats_run_seconds = self.config.getint(section, 'get_stats_run_seconds')

                            invalid_wan_ip = rfc1918_ip_check(fallback_ip)

                            if invalid_wan_ip:
                                self.logger.error('Invalid fallback_ip [%s] set for %s-%s!', fallback_ip, service,
                                                  server_id)
                                exit(1)

                            server = TautulliServer(id=server_id, url=scheme + url, api_key=apikey,
                                                    verify_ssl=verify_ssl, get_activity=get_activity,
                                                    fallback_ip=fallback_ip, get_stats=get_stats,
                                                    get_activity_run_seconds=get_activity_run_seconds,
                                                    get_stats_run_seconds=get_stats_run_seconds)

                        if service == 'ombi':
                            issue_status_counts = self.config.getboolean(section, 'get_issue_status_counts')
                            request_type_counts = self.config.getboolean(section, 'get_request_type_counts')
                            request_total_counts = self.config.getboolean(section, 'get_request_total_counts')

                            issue_status_run_seconds = self.config.getint(section, 'issue_status_run_seconds')
                            request_type_run_seconds = self.config.getint(section, 'request_type_run_seconds')
                            request_total_run_seconds = self.config.getint(section, 'request_total_run_seconds')

                            server = OmbiServer(id=server_id, url=scheme + url, api_key=apikey, verify_ssl=verify_ssl,
                                                request_type_counts=request_type_counts,
                                                request_type_run_seconds=request_type_run_seconds,
                                                request_total_counts=request_total_counts,
                                                request_total_run_seconds=request_total_run_seconds,
                                                issue_status_counts=issue_status_counts,
                                                issue_status_run_seconds=issue_status_run_seconds)

                        if service == 'sickchill':
                            get_missing = self.config.getboolean(section, 'get_missing')
                            get_missing_run_seconds = self.config.getint(section, 'get_missing_run_seconds')

                            server = SickChillServer(id=server_id, url=scheme + url, api_key=apikey,
                                                     verify_ssl=verify_ssl, get_missing=get_missing,
                                                     get_missing_run_seconds=get_missing_run_seconds)

                        if service == 'unifi':
                            username = self.config.get(section, 'username')
                            password = self.config.get(section, 'password')
                            site = self.config.get(section, 'site').lower()
                            usg_name = self.config.get(section, 'usg_name')
                            get_usg_stats_run_seconds = self.config.getint(section, 'get_usg_stats_run_seconds')

                            server = UniFiServer(id=server_id, url=scheme + url, verify_ssl=verify_ssl, site=site,
                                                 username=username, password=password, usg_name=usg_name,
                                                 get_usg_stats_run_seconds=get_usg_stats_run_seconds)

                        getattr(self, f'{service}_servers').append(server)
                    except NoOptionError as e:
                        self.logger.error('Missing key in %s. Error: %s', section, e)
                        self.rectify_ini()
                        return
