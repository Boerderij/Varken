import platform
import schedule
import distro
from time import sleep
from queue import Queue
from sys import version
from threading import Thread
from os import environ as env
from os import access, R_OK, getenv
from os.path import isdir, abspath, dirname, join
from argparse import ArgumentParser, RawTextHelpFormatter
from logging import getLogger, StreamHandler, Formatter, DEBUG


# Needed to check version of python
from varken import structures  # noqa
from varken.ombi import OmbiAPI
from varken.overseerr import OverseerrAPI
from varken.unifi import UniFiAPI
from varken import VERSION, BRANCH, BUILD_DATE
from varken.sonarr import SonarrAPI
from varken.radarr import RadarrAPI
from varken.lidarr import LidarrAPI
from varken.iniparser import INIParser
from varken.dbmanager import DBManager
from varken.helpers import GeoIPHandler
from varken.tautulli import TautulliAPI
from varken.sickchill import SickChillAPI
from varken.varkenlogger import VarkenLogger


PLATFORM_LINUX_DISTRO = ' '.join(distro.id() + distro.version() + distro.name())


def thread(job, **kwargs):
    worker = Thread(target=job, kwargs=dict(**kwargs))
    worker.start()


if __name__ == "__main__":
    parser = ArgumentParser(prog='varken',
                            description='Command-line utility to aggregate data from the plex ecosystem into InfluxDB',
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-d", "--data-folder", help='Define an alternate data folder location')
    parser.add_argument("-D", "--debug", action='store_true', help='Use to enable DEBUG logging. (Depreciated)')
    parser.add_argument("-ND", "--no_debug", action='store_true', help='Use to disable DEBUG logging')

    opts = parser.parse_args()

    templogger = getLogger('temp')
    templogger.setLevel(DEBUG)
    tempch = StreamHandler()
    tempformatter = Formatter('%(asctime)s : %(levelname)s : %(module)s : %(message)s', '%Y-%m-%d %H:%M:%S')
    tempch.setFormatter(tempformatter)
    templogger.addHandler(tempch)

    DATA_FOLDER = env.get('DATA_FOLDER', vars(opts).get('data_folder') or abspath(join(dirname(__file__), 'data')))

    if isdir(DATA_FOLDER):
        if not access(DATA_FOLDER, R_OK):
            templogger.error("Read permission error for %s", DATA_FOLDER)
            exit(1)
    else:
        templogger.error("%s does not exist", DATA_FOLDER)
        exit(1)

    # Set Debug to True if DEBUG env is set
    enable_opts = ['True', 'true', 'yes']
    debug_opts = ['debug', 'Debug', 'DEBUG']

    opts.debug = True

    if getenv('DEBUG') is not None:
        opts.debug = True if any([getenv(string, False) for true in enable_opts
                                  for string in debug_opts if getenv(string, False) == true]) else False

    elif opts.no_debug:
        opts.debug = False

    # Initiate the logger
    vl = VarkenLogger(data_folder=DATA_FOLDER, debug=opts.debug)
    vl.logger.info('Starting Varken...')

    vl.logger.info('Data folder is "%s"', DATA_FOLDER)

    vl.logger.info(u"%s %s (%s%s)", platform.system(), platform.release(), platform.version(),
                   ' - ' + PLATFORM_LINUX_DISTRO if PLATFORM_LINUX_DISTRO else '')

    vl.logger.info(u"Python %s", version)

    vl.logger.info("Varken v%s-%s %s", VERSION, BRANCH, BUILD_DATE)

    CONFIG = INIParser(DATA_FOLDER)
    DBMANAGER = DBManager(CONFIG.influx_server)
    QUEUE = Queue()

    if CONFIG.sonarr_enabled:
        for server in CONFIG.sonarr_servers:
            SONARR = SonarrAPI(server, DBMANAGER)
            if server.queue:
                at_time = schedule.every(server.queue_run_seconds).seconds
                at_time.do(thread, SONARR.get_queue).tag("sonarr-{}-get_queue".format(server.id))
            if server.missing_days > 0:
                at_time = schedule.every(server.missing_days_run_seconds).seconds
                at_time.do(thread, SONARR.get_calendar, query="Missing").tag("sonarr-{}-get_missing".format(server.id))
            if server.future_days > 0:
                at_time = schedule.every(server.future_days_run_seconds).seconds
                at_time.do(thread, SONARR.get_calendar, query="Future").tag("sonarr-{}-get_future".format(server.id))

    if CONFIG.tautulli_enabled:
        GEOIPHANDLER = GeoIPHandler(DATA_FOLDER, CONFIG.tautulli_servers[0].maxmind_license_key)
        schedule.every(12).to(24).hours.do(thread, GEOIPHANDLER.update)
        for server in CONFIG.tautulli_servers:
            TAUTULLI = TautulliAPI(server, DBMANAGER, GEOIPHANDLER)
            if server.get_activity:
                at_time = schedule.every(server.get_activity_run_seconds).seconds
                at_time.do(thread, TAUTULLI.get_activity).tag("tautulli-{}-get_activity".format(server.id))
            if server.get_stats:
                at_time = schedule.every(server.get_stats_run_seconds).seconds
                at_time.do(thread, TAUTULLI.get_stats).tag("tautulli-{}-get_stats".format(server.id))

    if CONFIG.radarr_enabled:
        for server in CONFIG.radarr_servers:
            RADARR = RadarrAPI(server, DBMANAGER)
            if server.get_missing:
                at_time = schedule.every(server.get_missing_run_seconds).seconds
                at_time.do(thread, RADARR.get_missing).tag("radarr-{}-get_missing".format(server.id))
            if server.queue:
                at_time = schedule.every(server.queue_run_seconds).seconds
                at_time.do(thread, RADARR.get_queue).tag("radarr-{}-get_queue".format(server.id))

    if CONFIG.lidarr_enabled:
        for server in CONFIG.lidarr_servers:
            LIDARR = LidarrAPI(server, DBMANAGER)
            if server.queue:
                at_time = schedule.every(server.queue_run_seconds).seconds
                at_time.do(thread, LIDARR.get_queue).tag("lidarr-{}-get_queue".format(server.id))
            if server.missing_days > 0:
                at_time = schedule.every(server.missing_days_run_seconds).seconds
                at_time.do(thread, LIDARR.get_calendar, query="Missing").tag(
                    "lidarr-{}-get_missing".format(server.id))
            if server.future_days > 0:
                at_time = schedule.every(server.future_days_run_seconds).seconds
                at_time.do(thread, LIDARR.get_calendar, query="Future").tag("lidarr-{}-get_future".format(
                    server.id))

    if CONFIG.ombi_enabled:
        for server in CONFIG.ombi_servers:
            OMBI = OmbiAPI(server, DBMANAGER)
            if server.request_type_counts:
                at_time = schedule.every(server.request_type_run_seconds).seconds
                at_time.do(thread, OMBI.get_request_counts).tag("ombi-{}-get_request_counts".format(server.id))
            if server.request_total_counts:
                at_time = schedule.every(server.request_total_run_seconds).seconds
                at_time.do(thread, OMBI.get_all_requests).tag("ombi-{}-get_all_requests".format(server.id))
            if server.issue_status_counts:
                at_time = schedule.every(server.issue_status_run_seconds).seconds
                at_time.do(thread, OMBI.get_issue_counts).tag("ombi-{}-get_issue_counts".format(server.id))

    if CONFIG.overseerr_enabled:
        for server in CONFIG.overseerr_servers:
            OVERSEER = OverseerrAPI(server, DBMANAGER)
            if server.get_request_total_counts:
                at_time = schedule.every(server.request_total_run_seconds).seconds
                at_time.do(thread, OVERSEER.get_request_counts).tag("overseerr-{}-get_request_counts"
                                                                    .format(server.id))
            if server.num_latest_requests_to_fetch > 0:
                at_time = schedule.every(server.num_latest_requests_seconds).seconds
                at_time.do(thread, OVERSEER.get_latest_requests).tag("overseerr-{}-get_latest_requests"
                                                                     .format(server.id))

    if CONFIG.sickchill_enabled:
        for server in CONFIG.sickchill_servers:
            SICKCHILL = SickChillAPI(server, DBMANAGER)
            if server.get_missing:
                at_time = schedule.every(server.get_missing_run_seconds).seconds
                at_time.do(thread, SICKCHILL.get_missing).tag("sickchill-{}-get_missing".format(server.id))

    if CONFIG.unifi_enabled:
        for server in CONFIG.unifi_servers:
            UNIFI = UniFiAPI(server, DBMANAGER)
            at_time = schedule.every(server.get_usg_stats_run_seconds).seconds
            at_time.do(thread, UNIFI.get_usg_stats).tag("unifi-{}-get_usg_stats".format(server.id))

    # Run all on startup
    SERVICES_ENABLED = [CONFIG.ombi_enabled, CONFIG.radarr_enabled, CONFIG.tautulli_enabled, CONFIG.unifi_enabled,
                        CONFIG.sonarr_enabled, CONFIG.sickchill_enabled, CONFIG.lidarr_enabled,
                        CONFIG.overseerr_enabled]
    if not [enabled for enabled in SERVICES_ENABLED if enabled]:
        vl.logger.error("All services disabled. Exiting")
        exit(1)

    schedule.run_all()

    while schedule.jobs:
        schedule.run_pending()
        sleep(1)
