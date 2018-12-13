import os
import time
import tarfile
import hashlib
import urllib3
import geoip2.database
import logging

from json.decoder import JSONDecodeError
from os.path import abspath, join
from requests.exceptions import InvalidSchema, SSLError, ConnectionError
from urllib.request import urlretrieve

logger = logging.getLogger('varken')


def geoip_download(data_folder):
    datafolder = data_folder

    tar_dbfile = abspath(join(datafolder, 'GeoLite2-City.tar.gz'))

    url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'
    logger.info('Downloading GeoLite2 from %s', url)
    urlretrieve(url, tar_dbfile)

    tar = tarfile.open(tar_dbfile, 'r:gz')
    logging.debug('Opening GeoLite2 tar file : %s', tar_dbfile)

    for files in tar.getmembers():
        if 'GeoLite2-City.mmdb' in files.name:
            logging.debug('"GeoLite2-City.mmdb" FOUND in tar file')
            files.name = os.path.basename(files.name)

            tar.extract(files, datafolder)
            logging.debug('%s has been extracted to %s', files, datafolder)

    os.remove(tar_dbfile)


def geo_lookup(ipaddress, data_folder):
    datafolder = data_folder
    logging.debug('Reading GeoLite2 DB from %s', datafolder)

    dbfile = abspath(join(datafolder, 'GeoLite2-City.mmdb'))
    now = time.time()

    try:
        dbinfo = os.stat(dbfile)
        db_age = now - dbinfo.st_ctime
        if db_age > (35 * 86400):
            logging.info('GeoLite2 DB is older than 35 days. Attempting to re-download...')

            os.remove(dbfile)

            geoip_download(datafolder)
    except FileNotFoundError:
        logging.error('GeoLite2 DB not found. Attempting to download...')
        geoip_download(datafolder)

    reader = geoip2.database.Reader(dbfile)

    return reader.city(ipaddress)


def hashit(string):
    encoded = string.encode()
    hashed = hashlib.md5(encoded).hexdigest()

    return hashed


def connection_handler(session, request, verify):
    s = session
    r = request
    v = verify
    return_json = False

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        logger.info('Creating folder %s ', path)
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.error('Could not create folder %s : %s ', path, e)


def clean_sid_check(server_id_list, server_type=None):
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
