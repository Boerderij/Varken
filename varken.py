import schedule
import threading
from sys import exit
from time import sleep
from os import access, R_OK
from os.path import isdir, abspath, dirname, join
from argparse import ArgumentParser, RawTextHelpFormatter

from Varken.iniparser import INIParser
from Varken.sonarr import SonarrAPI
from Varken.tautulli import TautulliAPI
from Varken.radarr import RadarrAPI
from Varken.ombi import OmbiAPI
from Varken.dbmanager import DBManager

def threaded(job):
    thread = threading.Thread(target=job)
    thread.start()


if __name__ == "__main__":
    parser = ArgumentParser(prog='Varken',
                            description='Command-line utility to aggregate data from the plex ecosystem into InfluxDB',
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-d", "--data-folder", help='Define an alternate data folder location')
    parser.add_argument("-l", "--log-level", choices=['info', 'error', 'debug'], help='Not yet implemented')

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
            TAUTULLI = TautulliAPI(server, DBMANAGER)
            if server.get_activity:
                schedule.every(server.get_activity_run_seconds).seconds.do(threaded, TAUTULLI.get_activity)
            if server.get_sessions:
                schedule.every(server.get_sessions_run_seconds).seconds.do(threaded, TAUTULLI.get_sessions)

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
                schedule.every(server.request_total_run_seconds).seconds.do(threaded, OMBI.get_total_requests)

    # Run all on startup
    schedule.run_all()

    while True:
        schedule.run_pending()
        sleep(1)
