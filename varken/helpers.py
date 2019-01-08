from hashlib import md5
from datetime import date
from logging import getLogger
from ipaddress import IPv4Address
from calendar import monthcalendar
from geoip2.database import Reader
from tarfile import open as taropen
from urllib3 import disable_warnings
from os import stat, remove, makedirs
from urllib.request import urlretrieve
from json.decoder import JSONDecodeError
from os.path import abspath, join, basename, isdir
from urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import InvalidSchema, SSLError, ConnectionError

logger = getLogger()


class GeoIPHandler(object):
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.dbfile = abspath(join(self.data_folder, 'GeoLite2-City.mmdb'))
        self.logger = getLogger()
        self.update()

        self.logger.info('Opening persistent connection to GeoLite2 DB...')
        self.reader = Reader(self.dbfile)

    def lookup(self, ipaddress):
        ip = ipaddress
        self.logger.debug('Getting lat/long for Tautulli stream using ip with last octet ending in %s',
                          ip.split('.')[-1:][0])
        return self.reader.city(ip)

    def update(self):
        today = date.today()

        try:
            dbdate = date.fromtimestamp(stat(self.dbfile).st_ctime)
        except FileNotFoundError:
            self.logger.error("Could not find GeoLite2 DB as: %s", self.dbfile)
            self.download()
            dbdate = date.fromtimestamp(stat(self.dbfile).st_ctime)

        first_wednesday_day = [week[2:3][0] for week in monthcalendar(today.year, today.month) if week[2:3][0] != 0][0]
        first_wednesday_date = date(today.year, today.month, first_wednesday_day)

        if dbdate < first_wednesday_date < today:
            self.logger.info("Newer GeoLite2 DB available, Updating...")
            remove(self.dbfile)
            self.download()
        else:
            td = first_wednesday_date - today
            if td.days < 0:
                self.logger.debug('Geolite2 DB is only %s days old. Keeping current copy', abs(td.days))
            else:
                self.logger.debug('Geolite2 DB will update in %s days', abs(td.days))

    def download(self):
        tar_dbfile = abspath(join(self.data_folder, 'GeoLite2-City.tar.gz'))
        url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'

        self.logger.info('Downloading GeoLite2 from %s', url)
        urlretrieve(url, tar_dbfile)

        self.logger.debug('Opening GeoLite2 tar file : %s', tar_dbfile)

        tar = taropen(tar_dbfile, 'r:gz')

        for files in tar.getmembers():
            if 'GeoLite2-City.mmdb' in files.name:
                self.logger.debug('"GeoLite2-City.mmdb" FOUND in tar file')
                files.name = basename(files.name)
                tar.extract(files, self.data_folder)
                self.logger.debug('%s has been extracted to %s', files, self.data_folder)
        tar.close()
        remove(tar_dbfile)


def hashit(string):
    encoded = string.encode()
    hashed = md5(encoded).hexdigest()

    return hashed


def rfc1918_ip_check(ip):
    rfc1918_ip = IPv4Address(ip).is_private

    return rfc1918_ip


def connection_handler(session, request, verify, as_is_reply=False):
    air = as_is_reply
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

        if air:
            return get
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
        if not isdir(path):
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
