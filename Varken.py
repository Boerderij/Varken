import sys

# Check for python3.6 or newer to resolve erroneous typing.NamedTuple issues
if sys.version_info < (3, 6):
    exit('Varken requires python3.6 or newer')

import schedule
import threading
import platform
import distro
import os

from sys import exit
from time import sleep
from os import access, R_OK
from os.path import isdir, abspath, dirname, join
from argparse import ArgumentParser, RawTextHelpFormatter

from varken.iniparser import INIParser
from varken.sonarr import SonarrAPI
from varken.tautulli import TautulliAPI
from varken.radarr import RadarrAPI
from varken.ombi import OmbiAPI
from varken.cisco import CiscoAPI
from varken.dbmanager import DBManager
from varken.varkenlogger import VarkenLogger

PLATFORM_LINUX_DISTRO = ' '.join(x for x in distro.linux_distribution() if x)


def threaded(job):
    thread = threading.Thread(target=job)
    thread.start()


if __name__ == "__main__":
    parser = ArgumentParser(prog='varken',
                            description='Command-line utility to aggregate data from the plex ecosystem into InfluxDB',
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-d", "--data-folder", help='Define an alternate data folder location')
    parser.add_argument("-D", "--debug", action='store_true', help='Use to enable DEBUG logging')

    opts = parser.parse_args()

    DATA_FOLDER = abspath(join(dirname(__file__), 'data'))

    if opts.data_folder:
        ARG_FOLDER = opts.data_folder

        if isdir(ARG_FOLDER):
            DATA_FOLDER = ARG_FOLDER
            if not access(ARG_FOLDER, R_OK):
                exit("Read permission error for {}".format(ARG_FOLDER))
        else:
            exit("{} does not exist".format(ARG_FOLDER))

    # Set Debug to True if DEBUG env is set
    enable_opts = ['True', 'true', 'yes']
    debug_opts = ['debug', 'Debug', 'DEBUG']

    if not opts.debug:
        opts.debug = True if any([os.getenv(string, False) for true in enable_opts
                                  for string in debug_opts if os.getenv(string, False) == true]) else False

    # Initiate the logger
    vl = VarkenLogger(data_folder=DATA_FOLDER, debug=opts.debug)
    vl.logger.info('Starting Varken...')

    vl.logger.info('Data folder is "%s"', DATA_FOLDER)

    vl.logger.info(u"{} {} ({}{})".format(
            platform.system(), platform.release(), platform.version(),
            ' - {}'.format(PLATFORM_LINUX_DISTRO) if PLATFORM_LINUX_DISTRO else ''
        ))
    vl.logger.info(u"Python {}".format(sys.version))

    CONFIG = INIParser(DATA_FOLDER)
    DBMANAGER = DBManager(CONFIG.influx_server)

    if CONFIG.sonarr_enabled:
        for server in CONFIG.sonarr_servers:
            SONARR = SonarrAPI(server, DBMANAGER)
            if server.queue:
                schedule.every(server.queue_run_seconds).seconds.do(threaded, SONARR.get_queue)
            if server.missing_days > 0:
                schedule.every(server.missing_days_run_seconds).seconds.do(threaded, SONARR.get_missing)
            if server.future_days > 0:
                schedule.every(server.future_days_run_seconds).seconds.do(threaded, SONARR.get_future)

    if CONFIG.tautulli_enabled:
        for server in CONFIG.tautulli_servers:
            TAUTULLI = TautulliAPI(server, DBMANAGER, DATA_FOLDER)
            if server.get_activity:
                schedule.every(server.get_activity_run_seconds).seconds.do(threaded, TAUTULLI.get_activity)

    if CONFIG.radarr_enabled:
        for server in CONFIG.radarr_servers:
            RADARR = RadarrAPI(server, DBMANAGER)
            if server.get_missing:
                schedule.every(server.get_missing_run_seconds).seconds.do(threaded, RADARR.get_missing)
            if server.queue:
                schedule.every(server.queue_run_seconds).seconds.do(threaded, RADARR.get_queue)

    if CONFIG.ombi_enabled:
        for server in CONFIG.ombi_servers:
            OMBI = OmbiAPI(server, DBMANAGER)
            if server.request_type_counts:
                schedule.every(server.request_type_run_seconds).seconds.do(threaded, OMBI.get_request_counts)
            if server.request_total_counts:
                schedule.every(server.request_total_run_seconds).seconds.do(threaded, OMBI.get_all_requests)

    if CONFIG.ciscoasa_enabled:
        for firewall in CONFIG.ciscoasa_firewalls:
            ASA = CiscoAPI(firewall, DBMANAGER)
            schedule.every(firewall.get_bandwidth_run_seconds).seconds.do(threaded, ASA.get_bandwidth)

    # Run all on startup
    SERVICES_ENABLED = [CONFIG.ombi_enabled, CONFIG.radarr_enabled, CONFIG.tautulli_enabled,
                        CONFIG.sonarr_enabled, CONFIG.ciscoasa_enabled]
    if not [enabled for enabled in SERVICES_ENABLED if enabled]:
        exit("All services disabled. Exiting")
    schedule.run_all()

    while True:
        schedule.run_pending()
        sleep(1)
