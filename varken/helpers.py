from hashlib import md5
from datetime import date, timedelta
from time import sleep
from logging import getLogger
from ipaddress import IPv4Address
from urllib.error import HTTPError, URLError
from geoip2.database import Reader
from tarfile import open as taropen
from urllib3 import disable_warnings
from os import stat, remove, makedirs
from urllib.request import urlretrieve
from json.decoder import JSONDecodeError
from os.path import abspath, join, basename, isdir
from urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import InvalidSchema, SSLError, ConnectionError, ChunkedEncodingError

logger = getLogger()


class GeoIPHandler(object):
    def __init__(self, data_folder, maxmind_license_key):
        self.data_folder = data_folder
        self.maxmind_license_key = maxmind_license_key
        self.dbfile = abspath(join(self.data_folder, 'GeoLite2-City.mmdb'))
        self.logger = getLogger()
        self.reader = None
        self.reader_manager(action='open')

        self.logger.info('Opening persistent connection to the MaxMind DB...')

    def reader_manager(self, action=None):
        if action == 'open':
            try:
                self.reader = Reader(self.dbfile)
            except FileNotFoundError:
                self.logger.error("Could not find MaxMind DB! Downloading!")
                result_status = self.download()
                if result_status:
                    self.logger.error("Could not download MaxMind DB! You may need to manually install it.")
                    exit(1)
                else:
                    self.reader = Reader(self.dbfile)
        else:
            self.reader.close()

    def lookup(self, ipaddress):
        ip = ipaddress
        self.logger.debug('Getting lat/long for Tautulli stream using ip with last octet ending in %s',
                          ip.split('.')[-1:][0])
        return self.reader.city(ip)

    def update(self):
        today = date.today()

        try:
            dbdate = date.fromtimestamp(stat(self.dbfile).st_mtime)
            db_next_update = date.fromtimestamp(stat(self.dbfile).st_mtime) + timedelta(days=30)

        except FileNotFoundError:
            self.logger.error("Could not find MaxMind DB as: %s", self.dbfile)
            self.download()
            dbdate = date.fromtimestamp(stat(self.dbfile).st_mtime)
            db_next_update = date.fromtimestamp(stat(self.dbfile).st_mtime) + timedelta(days=30)

        if db_next_update < today:
            self.logger.info("Newer MaxMind DB available, Updating...")
            self.logger.debug("MaxMind DB date %s, DB updates after: %s, Today: %s",
                              dbdate, db_next_update, today)
            self.reader_manager(action='close')
            self.download()
            self.reader_manager(action='open')
        else:
            db_days_update = db_next_update - today
            self.logger.debug("MaxMind DB will update in %s days", abs(db_days_update.days))
            self.logger.debug("MaxMind DB date %s, DB updates after: %s, Today: %s",
                              dbdate, db_next_update, today)

    def download(self):
        tar_dbfile = abspath(join(self.data_folder, 'GeoLite2-City.tar.gz'))
        maxmind_url = ('https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City'
                       f'&suffix=tar.gz&license_key={self.maxmind_license_key}')
        downloaded = False

        retry_counter = 0

        while not downloaded:
            self.logger.info('Downloading GeoLite2 DB from MaxMind...')
            try:
                urlretrieve(maxmind_url, tar_dbfile)
                downloaded = True
            except URLError as e:
                self.logger.error("Problem downloading new MaxMind DB: %s", e)
                result_status = 1
                return result_status
            except HTTPError as e:
                if e.code == 401:
                    self.logger.error("Your MaxMind license key is incorect! Check your config: %s", e)
                    result_status = 1
                    return result_status
                else:
                    self.logger.error("Problem downloading new MaxMind DB... Trying again: %s", e)
                    sleep(2)
                    retry_counter = (retry_counter + 1)

                if retry_counter >= 3:
                    self.logger.error("Retried downloading the new MaxMind DB 3 times and failed... Aborting!")
                    result_status = 1
                    return result_status
        try:
            remove(self.dbfile)
        except FileNotFoundError:
            self.logger.warning("Cannot remove MaxMind DB as it does not exist!")

        self.logger.debug("Opening MaxMind tar file : %s", tar_dbfile)

        tar = taropen(tar_dbfile, 'r:gz')

        for files in tar.getmembers():
            if 'GeoLite2-City.mmdb' in files.name:
                self.logger.debug('"GeoLite2-City.mmdb" FOUND in tar file')
                files.name = basename(files.name)
                tar.extract(files, self.data_folder)
                self.logger.debug('%s has been extracted to %s', files, self.data_folder)
        tar.close()
        try:
            remove(tar_dbfile)
            self.logger.debug('Removed the MaxMind DB tar file.')
        except FileNotFoundError:
            self.logger.warning("Cannot remove MaxMind DB TAR file as it does not exist!")


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
            if 'NoSiteContext' in str(get.content):
                logger.info('Your Site is incorrect for %s', r.url)
            elif 'LoginRequired' in str(get.content):
                logger.info('Your login credentials are incorrect for %s', r.url)
            else:
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
    except ChunkedEncodingError as e:
        logger.error('Broken connection during request... oops? Error: %s', e)

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


def boolcheck(var):
    if var.lower() in ['true', 'yes']:
        return True
    else:
        return False


def itemgetter_with_default(**defaults):
    return lambda obj: tuple(obj.get(k, v) for k, v in defaults.items())
