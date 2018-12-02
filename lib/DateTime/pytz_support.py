##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from datetime import datetime, timedelta

import pytz
import pytz.reference
from pytz.tzinfo import StaticTzInfo, memorized_timedelta

from .interfaces import DateTimeError

EPOCH = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)

_numeric_timezone_data = {
    'GMT':      ('GMT',      0, 1, [], '', [(0, 0, 0)],      'GMT\000'),
    'GMT+0':    ('GMT+0',    0, 1, [], '', [(0, 0, 0)],      'GMT+0000\000'),
    'GMT+1':    ('GMT+1',    0, 1, [], '', [(3600, 0, 0)],   'GMT+0100\000'),
    'GMT+2':    ('GMT+2',    0, 1, [], '', [(7200, 0, 0)],   'GMT+0200\000'),
    'GMT+3':    ('GMT+3',    0, 1, [], '', [(10800, 0, 0)],  'GMT+0300\000'),
    'GMT+4':    ('GMT+4',    0, 1, [], '', [(14400, 0, 0)],  'GMT+0400\000'),
    'GMT+5':    ('GMT+5',    0, 1, [], '', [(18000, 0, 0)],  'GMT+0500\000'),
    'GMT+6':    ('GMT+6',    0, 1, [], '', [(21600, 0, 0)],  'GMT+0600\000'),
    'GMT+7':    ('GMT+7',    0, 1, [], '', [(25200, 0, 0)],  'GMT+0700\000'),
    'GMT+8':    ('GMT+8',    0, 1, [], '', [(28800, 0, 0)],  'GMT+0800\000'),
    'GMT+9':    ('GMT+9',    0, 1, [], '', [(32400, 0, 0)],  'GMT+0900\000'),
    'GMT+10':   ('GMT+10',   0, 1, [], '', [(36000, 0, 0)],  'GMT+1000\000'),
    'GMT+11':   ('GMT+11',   0, 1, [], '', [(39600, 0, 0)],  'GMT+1100\000'),
    'GMT+12':   ('GMT+12',   0, 1, [], '', [(43200, 0, 0)],  'GMT+1200\000'),
    'GMT+13':   ('GMT+13',   0, 1, [], '', [(46800, 0, 0)],  'GMT+1300\000'),

    'GMT-1':    ('GMT-1',    0, 1, [], '', [(-3600, 0, 0)],  'GMT-0100\000'),
    'GMT-2':    ('GMT-2',    0, 1, [], '', [(-7200, 0, 0)],  'GMT-0200\000'),
    'GMT-3':    ('GMT-3',    0, 1, [], '', [(-10800, 0, 0)], 'GMT-0300\000'),
    'GMT-4':    ('GMT-4',    0, 1, [], '', [(-14400, 0, 0)], 'GMT-0400\000'),
    'GMT-5':    ('GMT-5',    0, 1, [], '', [(-18000, 0, 0)], 'GMT-0500\000'),
    'GMT-6':    ('GMT-6',    0, 1, [], '', [(-21600, 0, 0)], 'GMT-0600\000'),
    'GMT-7':    ('GMT-7',    0, 1, [], '', [(-25200, 0, 0)], 'GMT-0700\000'),
    'GMT-8':    ('GMT-8',    0, 1, [], '', [(-28800, 0, 0)], 'GMT-0800\000'),
    'GMT-9':    ('GMT-9',    0, 1, [], '', [(-32400, 0, 0)], 'GMT-0900\000'),
    'GMT-10':   ('GMT-10',   0, 1, [], '', [(-36000, 0, 0)], 'GMT-1000\000'),
    'GMT-11':   ('GMT-11',   0, 1, [], '', [(-39600, 0, 0)], 'GMT-1100\000'),
    'GMT-12':   ('GMT-12',   0, 1, [], '', [(-43200, 0, 0)], 'GMT-1200\000'),

    'GMT+0130': ('GMT+0130', 0, 1, [], '', [(5400,  0, 0)],  'GMT+0130\000'),
    'GMT+0230': ('GMT+0230', 0, 1, [], '', [(9000,  0, 0)],  'GMT+0230\000'),
    'GMT+0330': ('GMT+0330', 0, 1, [], '', [(12600, 0, 0)],  'GMT+0330\000'),
    'GMT+0430': ('GMT+0430', 0, 1, [], '', [(16200, 0, 0)],  'GMT+0430\000'),
    'GMT+0530': ('GMT+0530', 0, 1, [], '', [(19800, 0, 0)],  'GMT+0530\000'),
    'GMT+0630': ('GMT+0630', 0, 1, [], '', [(23400, 0, 0)],  'GMT+0630\000'),
    'GMT+0730': ('GMT+0730', 0, 1, [], '', [(27000, 0, 0)],  'GMT+0730\000'),
    'GMT+0830': ('GMT+0830', 0, 1, [], '', [(30600, 0, 0)],  'GMT+0830\000'),
    'GMT+0930': ('GMT+0930', 0, 1, [], '', [(34200, 0, 0)],  'GMT+0930\000'),
    'GMT+1030': ('GMT+1030', 0, 1, [], '', [(37800, 0, 0)],  'GMT+1030\000'),
    'GMT+1130': ('GMT+1130', 0, 1, [], '', [(41400, 0, 0)],  'GMT+1130\000'),
    'GMT+1230': ('GMT+1230', 0, 1, [], '', [(45000, 0, 0)],  'GMT+1230\000'),

    'GMT-0130': ('GMT-0130', 0, 1, [], '', [(-5400,  0, 0)], 'GMT-0130\000'),
    'GMT-0230': ('GMT-0230', 0, 1, [], '', [(-9000,  0, 0)], 'GMT-0230\000'),
    'GMT-0330': ('GMT-0330', 0, 1, [], '', [(-12600, 0, 0)], 'GMT-0330\000'),
    'GMT-0430': ('GMT-0430', 0, 1, [], '', [(-16200, 0, 0)], 'GMT-0430\000'),
    'GMT-0530': ('GMT-0530', 0, 1, [], '', [(-19800, 0, 0)], 'GMT-0530\000'),
    'GMT-0630': ('GMT-0630', 0, 1, [], '', [(-23400, 0, 0)], 'GMT-0630\000'),
    'GMT-0730': ('GMT-0730', 0, 1, [], '', [(-27000, 0, 0)], 'GMT-0730\000'),
    'GMT-0830': ('GMT-0830', 0, 1, [], '', [(-30600, 0, 0)], 'GMT-0830\000'),
    'GMT-0930': ('GMT-0930', 0, 1, [], '', [(-34200, 0, 0)], 'GMT-0930\000'),
    'GMT-1030': ('GMT-1030', 0, 1, [], '', [(-37800, 0, 0)], 'GMT-1030\000'),
    'GMT-1130': ('GMT-1130', 0, 1, [], '', [(-41400, 0, 0)], 'GMT-1130\000'),
    'GMT-1230': ('GMT-1230', 0, 1, [], '', [(-45000, 0, 0)], 'GMT-1230\000'),
}

# These are the timezones not in pytz.common_timezones
_old_zlst = [
    'AST', 'AT', 'BST', 'BT', 'CCT',
    'CET', 'CST', 'Cuba', 'EADT', 'EAST',
    'EEST', 'EET', 'EST', 'Egypt', 'FST',
    'FWT', 'GB-Eire', 'GMT+0100', 'GMT+0130', 'GMT+0200',
    'GMT+0230', 'GMT+0300', 'GMT+0330', 'GMT+0400', 'GMT+0430',
    'GMT+0500', 'GMT+0530', 'GMT+0600', 'GMT+0630', 'GMT+0700',
    'GMT+0730', 'GMT+0800', 'GMT+0830', 'GMT+0900', 'GMT+0930',
    'GMT+1', 'GMT+1000', 'GMT+1030', 'GMT+1100', 'GMT+1130',
    'GMT+1200', 'GMT+1230', 'GMT+1300', 'GMT-0100', 'GMT-0130',
    'GMT-0200', 'GMT-0300', 'GMT-0400', 'GMT-0500', 'GMT-0600',
    'GMT-0630', 'GMT-0700', 'GMT-0730', 'GMT-0800', 'GMT-0830',
    'GMT-0900', 'GMT-0930', 'GMT-1000', 'GMT-1030', 'GMT-1100',
    'GMT-1130', 'GMT-1200', 'GMT-1230', 'GST', 'Greenwich',
    'Hongkong', 'IDLE', 'IDLW', 'Iceland', 'Iran',
    'Israel', 'JST', 'Jamaica', 'Japan', 'MEST',
    'MET', 'MEWT', 'MST', 'NT', 'NZDT',
    'NZST', 'NZT', 'PST', 'Poland', 'SST',
    'SWT', 'Singapore', 'Turkey', 'UCT', 'UT',
    'Universal', 'WADT', 'WAST', 'WAT', 'WET',
    'ZP4', 'ZP5', 'ZP6',
]

_old_zmap = {
    'aest': 'GMT+10', 'aedt': 'GMT+11',
    'aus eastern standard time': 'GMT+10',
    'sydney standard time': 'GMT+10',
    'tasmania standard time': 'GMT+10',
    'e. australia standard time': 'GMT+10',
    'aus central standard time': 'GMT+0930',
    'cen. australia standard time': 'GMT+0930',
    'w. australia standard time': 'GMT+8',

    'central europe standard time': 'GMT+1',
    'eastern standard time': 'US/Eastern',
    'us eastern standard time': 'US/Eastern',
    'central standard time': 'US/Central',
    'mountain standard time': 'US/Mountain',
    'pacific standard time': 'US/Pacific',
    'mst': 'US/Mountain', 'pst': 'US/Pacific',
    'cst': 'US/Central', 'est': 'US/Eastern',

    'gmt+0000': 'GMT+0', 'gmt+0': 'GMT+0',

    'gmt+0100': 'GMT+1', 'gmt+0200': 'GMT+2', 'gmt+0300': 'GMT+3',
    'gmt+0400': 'GMT+4', 'gmt+0500': 'GMT+5', 'gmt+0600': 'GMT+6',
    'gmt+0700': 'GMT+7', 'gmt+0800': 'GMT+8', 'gmt+0900': 'GMT+9',
    'gmt+1000': 'GMT+10', 'gmt+1100': 'GMT+11', 'gmt+1200': 'GMT+12',
    'gmt+1300': 'GMT+13',
    'gmt-0100': 'GMT-1', 'gmt-0200': 'GMT-2', 'gmt-0300': 'GMT-3',
    'gmt-0400': 'GMT-4', 'gmt-0500': 'GMT-5', 'gmt-0600': 'GMT-6',
    'gmt-0700': 'GMT-7', 'gmt-0800': 'GMT-8', 'gmt-0900': 'GMT-9',
    'gmt-1000': 'GMT-10', 'gmt-1100': 'GMT-11', 'gmt-1200': 'GMT-12',

    'gmt+1': 'GMT+1', 'gmt+2': 'GMT+2', 'gmt+3': 'GMT+3',
    'gmt+4': 'GMT+4', 'gmt+5': 'GMT+5', 'gmt+6': 'GMT+6',
    'gmt+7': 'GMT+7', 'gmt+8': 'GMT+8', 'gmt+9': 'GMT+9',
    'gmt+10': 'GMT+10', 'gmt+11': 'GMT+11', 'gmt+12': 'GMT+12',
    'gmt+13': 'GMT+13',
    'gmt-1': 'GMT-1', 'gmt-2': 'GMT-2', 'gmt-3': 'GMT-3',
    'gmt-4': 'GMT-4', 'gmt-5': 'GMT-5', 'gmt-6': 'GMT-6',
    'gmt-7': 'GMT-7', 'gmt-8': 'GMT-8', 'gmt-9': 'GMT-9',
    'gmt-10': 'GMT-10', 'gmt-11': 'GMT-11', 'gmt-12': 'GMT-12',

    'gmt+130': 'GMT+0130', 'gmt+0130': 'GMT+0130',
    'gmt+230': 'GMT+0230', 'gmt+0230': 'GMT+0230',
    'gmt+330': 'GMT+0330', 'gmt+0330': 'GMT+0330',
    'gmt+430': 'GMT+0430', 'gmt+0430': 'GMT+0430',
    'gmt+530': 'GMT+0530', 'gmt+0530': 'GMT+0530',
    'gmt+630': 'GMT+0630', 'gmt+0630': 'GMT+0630',
    'gmt+730': 'GMT+0730', 'gmt+0730': 'GMT+0730',
    'gmt+830': 'GMT+0830', 'gmt+0830': 'GMT+0830',
    'gmt+930': 'GMT+0930', 'gmt+0930': 'GMT+0930',
    'gmt+1030': 'GMT+1030',
    'gmt+1130': 'GMT+1130',
    'gmt+1230': 'GMT+1230',

    'gmt-130': 'GMT-0130', 'gmt-0130': 'GMT-0130',
    'gmt-230': 'GMT-0230', 'gmt-0230': 'GMT-0230',
    'gmt-330': 'GMT-0330', 'gmt-0330': 'GMT-0330',
    'gmt-430': 'GMT-0430', 'gmt-0430': 'GMT-0430',
    'gmt-530': 'GMT-0530', 'gmt-0530': 'GMT-0530',
    'gmt-630': 'GMT-0630', 'gmt-0630': 'GMT-0630',
    'gmt-730': 'GMT-0730', 'gmt-0730': 'GMT-0730',
    'gmt-830': 'GMT-0830', 'gmt-0830': 'GMT-0830',
    'gmt-930': 'GMT-0930', 'gmt-0930': 'GMT-0930',
    'gmt-1030': 'GMT-1030',
    'gmt-1130': 'GMT-1130',
    'gmt-1230': 'GMT-1230',

    'ut': 'Universal',
    'bst': 'GMT+1', 'mest': 'GMT+2', 'sst': 'GMT+2',
    'fst': 'GMT+2', 'wadt': 'GMT+8', 'eadt': 'GMT+11', 'nzdt': 'GMT+13',
    'wet': 'GMT', 'wat': 'GMT-1', 'at': 'GMT-2', 'ast': 'GMT-4',
    'nt': 'GMT-11', 'idlw': 'GMT-12', 'cet': 'GMT+1', 'cest': 'GMT+2',
    'met': 'GMT+1',
    'mewt': 'GMT+1', 'swt': 'GMT+1', 'fwt': 'GMT+1', 'eet': 'GMT+2',
    'eest': 'GMT+3',
    'bt': 'GMT+3', 'zp4': 'GMT+4', 'zp5': 'GMT+5', 'zp6': 'GMT+6',
    'wast': 'GMT+7', 'cct': 'GMT+8', 'jst': 'GMT+9', 'east': 'GMT+10',
    'gst': 'GMT+10', 'nzt': 'GMT+12', 'nzst': 'GMT+12', 'idle': 'GMT+12',
    'ret': 'GMT+4', 'ist': 'GMT+0530', 'edt': 'GMT-4',

}


# some timezone definitions of the "-0400" are not working
# when upgrading
for hour in range(0, 13):
    hour = hour
    fhour = str(hour)
    if len(fhour) == 1:
        fhour = '0' + fhour
    _old_zmap['-%s00' % fhour] = 'GMT-%i' % hour
    _old_zmap['+%s00' % fhour] = 'GMT+%i' % hour


def _static_timezone_factory(data):
    zone = data[0]
    cls = type(zone, (StaticTzInfo,), dict(
        zone=zone,
        _utcoffset=memorized_timedelta(data[5][0][0]),
        _tzname=data[6][:-1]))  # strip the trailing null
    return cls()

_numeric_timezones = dict((key, _static_timezone_factory(data))
                          for key, data in _numeric_timezone_data.items())


class Timezone:
    """
    Timezone information returned by PytzCache.__getitem__
    Adapts datetime.tzinfo object to DateTime._timezone interface
    """
    def __init__(self, tzinfo):
        self.tzinfo = tzinfo

    def info(self, t=None):
        if t is None:
            dt = datetime.utcnow().replace(tzinfo=pytz.utc)
        else:
            # can't use utcfromtimestamp past 2038
            dt = EPOCH + timedelta(0, t)

        # need to normalize tzinfo for the datetime to deal with
        # daylight savings time.
        normalized_dt = self.tzinfo.normalize(dt.astimezone(self.tzinfo))
        normalized_tzinfo = normalized_dt.tzinfo

        offset = normalized_tzinfo.utcoffset(normalized_dt)
        secs = offset.days * 24 * 60 * 60 + offset.seconds
        dst = normalized_tzinfo.dst(normalized_dt)
        if dst == timedelta(0):
            is_dst = 0
        else:
            is_dst = 1
        return secs, is_dst, normalized_tzinfo.tzname(normalized_dt)


class PytzCache:
    """
    Reimplementation of the DateTime._cache class that uses for timezone info
    """

    _zlst = pytz.common_timezones + _old_zlst  # used by DateTime.TimeZones
    _zmap = dict((name.lower(), name) for name in pytz.all_timezones)
    _zmap.update(_old_zmap)  # These must take priority
    _zidx = _zmap.keys()

    def __getitem__(self, key):
        name = self._zmap.get(key.lower(), key)  # fallback to key
        try:
            return Timezone(pytz.timezone(name))
        except pytz.UnknownTimeZoneError:
            try:
                return Timezone(_numeric_timezones[name])
            except KeyError:
                raise DateTimeError('Unrecognized timezone: %s' % key)
