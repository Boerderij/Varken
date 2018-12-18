from time import time
from hashlib import md5
from tarfile import open
from logging import getLogger
from geoip2.database import Reader
from urllib3 import disable_warnings
from os import stat, remove, makedirs
from urllib.request import urlretrieve
from json.decoder import JSONDecodeError
from os.path import abspath, join, basename
from urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import InvalidSchema, SSLError, ConnectionError

logger = getLogger()


def geoip_download(data_folder):
    datafolder = data_folder

    tar_dbfile = abspath(join(datafolder, 'GeoLite2-City.tar.gz'))

    url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'
    logger.info('Downloading GeoLite2 from %s', url)
    urlretrieve(url, tar_dbfile)

    tar = open(tar_dbfile, 'r:gz')
    logger.debug('Opening GeoLite2 tar file : %s', tar_dbfile)

    for files in tar.getmembers():
        if 'GeoLite2-City.mmdb' in files.name:
            logger.debug('"GeoLite2-City.mmdb" FOUND in tar file')
            files.name = basename(files.name)

            tar.extract(files, datafolder)
            logger.debug('%s has been extracted to %s', files, datafolder)

    remove(tar_dbfile)


def geo_lookup(ipaddress, data_folder):
    datafolder = data_folder
    logger.debug('Reading GeoLite2 DB from %s', datafolder)

    dbfile = abspath(join(datafolder, 'GeoLite2-City.mmdb'))
    now = time()

    try:
        dbinfo = stat(dbfile)
        db_age = now - dbinfo.st_ctime
        if db_age > (35 * 86400):
            logger.info('GeoLite2 DB is older than 35 days. Attempting to re-download...')

            remove(dbfile)

            geoip_download(datafolder)
    except FileNotFoundError:
        logger.error('GeoLite2 DB not found. Attempting to download...')
        geoip_download(datafolder)

    reader = Reader(dbfile)

    return reader.city(ipaddress)


def hashit(string):
    encoded = string.encode()
    hashed = md5(encoded).hexdigest()

    return hashed


def connection_handler(session, request, verify):
    s = session
    r = request
    v = verify
    return_json = False

    disable_warnings(InsecureRequestWarning)

    try:
        get = s.send(r, verify=v)
        if get.status_code == 401:
            logger.info('Your api key is incorrect for %s', r.url)
        elif get.status_code == 404:
            logger.info('This url doesnt even resolve: %s', r.url)
        elif get.status_code == 200:
            try:
                return_json = get.json()
            except JSONDecodeError:
                logger.error('No JSON response. Response is: %s', get.text)
        # 204 No Content is for ASA only
        elif get.status_code == 204:
            if get.headers['X-Auth-Token']:
                return get.headers['X-Auth-Token']

    except InvalidSchema:
        logger.error("You added http(s):// in the config file. Don't do that.")

    except SSLError as e:
        logger.error('Either your host is unreachable or you have an SSL issue. : %s', e)

    except ConnectionError as e:
        logger.error('Cannot resolve the url/ip/port. Check connectivity. Error: %s', e)

    return return_json


def mkdir_p(path):
    templogger = getLogger('temp')
    try:
        templogger.info('Creating folder %s ', path)
        makedirs(path, exist_ok=True)
    except Exception as e:
        templogger.error('Could not create folder %s : %s ', path, e)


def clean_sid_check(server_id_list, server_type=None):
    t = server_type
    sid_list = server_id_list
    cleaned_list = sid_list.replace(' ', '').split(',')
    valid_sids = []
    for sid in cleaned_list:
        try:
            valid_sids.append(int(sid))
        except ValueError:
            logger.error("%s is not a valid server id number", sid)
    if valid_sids:
        logger.info('%s : %s', t.upper(), valid_sids)
        return valid_sids
    else:
        logger.error('No valid %s', t.upper())
        return False
