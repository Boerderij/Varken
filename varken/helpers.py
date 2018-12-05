import os
import time
import tarfile
import hashlib
import geoip2.database
import logging

from json.decoder import JSONDecodeError
from os.path import abspath, join
from requests.exceptions import InvalidSchema, SSLError
from urllib.request import urlretrieve

logger = logging.getLogger('Varken')

def geoip_download():
    tar_dbfile = abspath(join('.', 'data', 'GeoLite2-City.tar.gz'))
    url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'
    urlretrieve(url, tar_dbfile)
    tar = tarfile.open(tar_dbfile, 'r:gz')
    for files in tar.getmembers():
        if 'GeoLite2-City.mmdb' in files.name:
            files.name = os.path.basename(files.name)
            tar.extract(files, abspath(join('.', 'data')))
    os.remove(tar_dbfile)


def geo_lookup(ipaddress):

    dbfile = abspath(join('.', 'data', 'GeoLite2-City.mmdb'))
    now = time.time()

    try:
        dbinfo = os.stat(dbfile)
        db_age = now - dbinfo.st_ctime
        if db_age > (35 * 86400):
            os.remove(dbfile)
            geoip_download()
    except FileNotFoundError:
        geoip_download()

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

    try:
        get = s.send(r, verify=v)
        if get.status_code == 401:
            logger.info('Your api key is incorrect for {}'.format(r.url))
        elif get.status_code == 404:
            logger.info('This url doesnt even resolve: {}'.format(r.url))
        elif get.status_code == 200:
            try:
                return_json = get.json()
            except JSONDecodeError:
                logger.info('No JSON response... BORKED! Let us know in discord')

    except InvalidSchema:
        logger.info('You added http(s):// in the config file. Don\'t do that.')

    except SSLError as e:
        logger.info('Either your host is unreachable or you have an ssl issue.')
        logger.info('The issue was: {}'.format(e))

    return return_json
