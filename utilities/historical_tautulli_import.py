#!/usr/bin/env python3
from argparse import ArgumentParser
from os import access, R_OK
from os.path import isdir, abspath, dirname, join
from logging import getLogger, StreamHandler, Formatter, DEBUG

from varken.iniparser import INIParser
from varken.dbmanager import DBManager
from varken.helpers import GeoIPHandler
from varken.tautulli import TautulliAPI

if __name__ == "__main__":
    parser = ArgumentParser(prog='varken',
                            description='Tautulli historical import tool')
    parser.add_argument("-d", "--data-folder", help='Define an alternate data folder location')
    parser.add_argument("-D", "--days", default=30, type=int, help='Specify length of historical import')
    opts = parser.parse_args()

    DATA_FOLDER = abspath(join(dirname(__file__), '..', 'data'))

    templogger = getLogger('temp')
    templogger.setLevel(DEBUG)
    tempch = StreamHandler()
    tempformatter = Formatter('%(asctime)s : %(levelname)s : %(module)s : %(message)s', '%Y-%m-%d %H:%M:%S')
    tempch.setFormatter(tempformatter)
    templogger.addHandler(tempch)

    if opts.data_folder:
        ARG_FOLDER = opts.data_folder

        if isdir(ARG_FOLDER):
            DATA_FOLDER = ARG_FOLDER
            if not access(DATA_FOLDER, R_OK):
                templogger.error("Read permission error for %s", DATA_FOLDER)
                exit(1)
        else:
            templogger.error("%s does not exist", ARG_FOLDER)
            exit(1)

    CONFIG = INIParser(DATA_FOLDER)
    DBMANAGER = DBManager(CONFIG.influx_server)

    if CONFIG.tautulli_enabled:
        GEOIPHANDLER = GeoIPHandler(DATA_FOLDER, CONFIG.tautulli_servers[0].maxmind_license_key)
        for server in CONFIG.tautulli_servers:
            TAUTULLI = TautulliAPI(server, DBMANAGER, GEOIPHANDLER)
            TAUTULLI.get_historical(days=opts.days)
