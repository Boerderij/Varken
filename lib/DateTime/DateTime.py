##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import math
import re
import sys
from time import altzone
from time import daylight
from time import gmtime
from time import localtime
from time import time
from time import timezone
from time import tzname
from datetime import datetime

from zope.interface import implementer

from .interfaces import IDateTime
from .interfaces import DateTimeError
from .interfaces import SyntaxError
from .interfaces import DateError
from .interfaces import TimeError
from .pytz_support import PytzCache

if sys.version_info > (3, ):
    import copyreg as copy_reg
    basestring = str
    long = int
    explicit_unicode_type = type(None)
else:
    import copy_reg
    explicit_unicode_type = unicode

default_datefmt = None


def getDefaultDateFormat():
    global default_datefmt
    if default_datefmt is None:
        try:
            from App.config import getConfiguration
            default_datefmt = getConfiguration().datetime_format
            return default_datefmt
        except Exception:
            return 'us'
    else:
        return default_datefmt

# To control rounding errors, we round system time to the nearest
# microsecond.  Then delicate calculations can rely on that the
# maximum precision that needs to be preserved is known.
_system_time = time


def time():
    return round(_system_time(), 6)

# Determine machine epoch
tm = ((0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334),
      (0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
yr, mo, dy, hr, mn, sc = gmtime(0)[:6]
i = int(yr - 1)
to_year = int(i * 365 + i // 4 - i // 100 + i // 400 - 693960.0)
to_month = tm[yr % 4 == 0 and (yr % 100 != 0 or yr % 400 == 0)][mo]
EPOCH = ((to_year + to_month + dy +
    (hr / 24.0 + mn / 1440.0 + sc / 86400.0)) * 86400)
jd1901 = 2415385

_TZINFO = PytzCache()

INT_PATTERN = re.compile(r'([0-9]+)')
FLT_PATTERN = re.compile(r':([0-9]+\.[0-9]+)')
NAME_PATTERN = re.compile(r'([a-zA-Z]+)', re.I)
SPACE_CHARS = ' \t\n'
DELIMITERS = '-/.:,+'

_MONTH_LEN = ((0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
              (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31))
_MONTHS = ('', 'January', 'February', 'March', 'April', 'May', 'June',
           'July', 'August', 'September', 'October', 'November', 'December')
_MONTHS_A = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
_MONTHS_P = ('', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June',
             'July', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.')
_MONTHMAP = {'january': 1, 'jan': 1,
             'february': 2, 'feb': 2,
             'march': 3, 'mar': 3,
             'april': 4, 'apr': 4,
             'may': 5,
             'june': 6, 'jun': 6,
             'july': 7, 'jul': 7,
             'august': 8, 'aug': 8,
             'september': 9, 'sep': 9, 'sept': 9,
             'october': 10, 'oct': 10,
             'november': 11, 'nov': 11,
             'december': 12, 'dec': 12}
_DAYS = ('Sunday', 'Monday', 'Tuesday', 'Wednesday',
         'Thursday', 'Friday', 'Saturday')
_DAYS_A = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
_DAYS_P = ('Sun.', 'Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.')
_DAYMAP = {'sunday': 1, 'sun': 1,
           'monday': 2, 'mon': 2,
           'tuesday': 3, 'tues': 3, 'tue': 3,
           'wednesday': 4, 'wed': 4,
           'thursday': 5, 'thurs': 5, 'thur': 5, 'thu': 5,
           'friday': 6, 'fri': 6,
           'saturday': 7, 'sat': 7}

numericTimeZoneMatch = re.compile(r'[+-][0-9][0-9][0-9][0-9]').match
iso8601Match = re.compile(r'''
  (?P<year>\d\d\d\d)                # four digits year
  (?:-?                             # one optional dash
   (?:                              # followed by:
    (?P<year_day>\d\d\d             #  three digits year day
     (?!\d))                        #  when there is no fourth digit
   |                                # or:
    W                               #  one W
    (?P<week>\d\d)                  #  two digits week
    (?:-?                           #  one optional dash
     (?P<week_day>\d)               #  one digit week day
    )?                              #  week day is optional
   |                                # or:
    (?P<month>\d\d)?                #  two digits month
    (?:-?                           #  one optional dash
     (?P<day>\d\d)?                 #  two digits day
    )?                              #  after day is optional
   )                                #
  )?                                # after year is optional
  (?:[T ]                           # one T or one whitespace
   (?P<hour>\d\d)                   # two digits hour
   (?::?                            # one optional colon
    (?P<minute>\d\d)?               # two digits minute
    (?::?                           # one optional colon
     (?P<second>\d\d)?              # two digits second
     (?:[.,]                        # one dot or one comma
      (?P<fraction>\d+)             # n digits fraction
     )?                             # after second is optional
    )?                              # after minute is optional
   )?                               # after hour is optional
   (?:                              # timezone:
    (?P<Z>Z)                        #  one Z
   |                                # or:
    (?P<signal>[-+])                #  one plus or one minus as signal
    (?P<hour_off>\d                 #  one digit for hour offset...
     (?:\d(?!\d$)                   #  ...or two, if not the last two digits
    )?)                             #  second hour offset digit is optional
    (?::?                           #  one optional colon
     (?P<min_off>\d\d)              #  two digits minute offset
    )?                              #  after hour offset is optional
   )?                               # timezone is optional
  )?                                # time is optional
  (?P<garbage>.*)                   # store the extra garbage
''', re.VERBOSE).match


def _findLocalTimeZoneName(isDST):
    if not daylight:
        # Daylight savings does not occur in this time zone.
        isDST = 0
    try:
        # Get the name of the current time zone depending
        # on DST.
        _localzone = PytzCache._zmap[tzname[isDST].lower()]
    except:
        try:
            # Generate a GMT-offset zone name.
            if isDST:
                localzone = altzone
            else:
                localzone = timezone
            offset = (-localzone / 3600.0)
            majorOffset = int(offset)
            if majorOffset != 0:
                minorOffset = abs(int((offset % majorOffset) * 60.0))
            else:
                minorOffset = 0
            m = majorOffset >= 0 and '+' or ''
            lz = '%s%0.02d%0.02d' % (m, majorOffset, minorOffset)
            _localzone = PytzCache._zmap[('GMT%s' % lz).lower()]
        except:
            _localzone = ''
    return _localzone

_localzone0 = _findLocalTimeZoneName(0)
_localzone1 = _findLocalTimeZoneName(1)
_multipleZones = (_localzone0 != _localzone1)

# Some utility functions for calculating dates:


def _calcSD(t):
    # Returns timezone-independent days since epoch and the fractional
    # part of the days.
    dd = t + EPOCH - 86400.0
    d = dd / 86400.0
    s = d - math.floor(d)
    return s, d


def _calcDependentSecond(tz, t):
    # Calculates the timezone-dependent second (integer part only)
    # from the timezone-independent second.
    fset = _tzoffset(tz, t)
    return fset + long(math.floor(t)) + long(EPOCH) - 86400


def _calcDependentSecond2(yr, mo, dy, hr, mn, sc):
    # Calculates the timezone-dependent second (integer part only)
    # from the date given.
    ss = int(hr) * 3600 + int(mn) * 60 + int(sc)
    x = long(_julianday(yr, mo, dy) - jd1901) * 86400 + ss
    return x


def _calcIndependentSecondEtc(tz, x, ms):
    # Derive the timezone-independent second from the timezone
    # dependent second.
    fsetAtEpoch = _tzoffset(tz, 0.0)
    nearTime = x - fsetAtEpoch - long(EPOCH) + 86400 + ms
    # nearTime is now within an hour of being correct.
    # Recalculate t according to DST.
    fset = long(_tzoffset(tz, nearTime))
    d = (x - fset) / 86400.0 + (ms / 86400.0)
    t = x - fset - long(EPOCH) + 86400 + ms
    micros = (x + 86400 - fset) * 1000000 + \
        long(round(ms * 1000000.0)) - long(EPOCH * 1000000.0)
    s = d - math.floor(d)
    return (s, d, t, micros)


def _calcHMS(x, ms):
    # hours, minutes, seconds from integer and float.
    hr = x // 3600
    x = x - hr * 3600
    mn = x // 60
    sc = x - mn * 60 + ms
    return (hr, mn, sc)


def _calcYMDHMS(x, ms):
    # x is a timezone-dependent integer of seconds.
    # Produces yr,mo,dy,hr,mn,sc.
    yr, mo, dy = _calendarday(x // 86400 + jd1901)
    x = int(x - (x // 86400) * 86400)
    hr = x // 3600
    x = x - hr * 3600
    mn = x // 60
    sc = x - mn * 60 + ms
    return (yr, mo, dy, hr, mn, sc)


def _julianday(yr, mo, dy):
    y, m, d = long(yr), long(mo), long(dy)
    if m > 12:
        y = y + m // 12
        m = m % 12
    elif m < 1:
        m = -m
        y = y - m // 12 - 1
        m = 12 - m % 12
    if y > 0:
        yr_correct = 0
    else:
        yr_correct = 3
    if m < 3:
        y, m = y - 1, m + 12
    if y * 10000 + m * 100 + d > 15821014:
        b = 2 - y // 100 + y // 400
    else:
        b = 0
    return ((1461 * y - yr_correct) // 4 +
        306001 * (m + 1) // 10000 + d + 1720994 + b)


def _calendarday(j):
    j = long(j)
    if (j < 2299160):
        b = j + 1525
    else:
        a = (4 * j - 7468861) // 146097
        b = j + 1526 + a - a // 4
    c = (20 * b - 2442) // 7305
    d = 1461 * c // 4
    e = 10000 * (b - d) // 306001
    dy = int(b - d - 306001 * e // 10000)
    mo = (e < 14) and int(e - 1) or int(e - 13)
    yr = (mo > 2) and (c - 4716) or (c - 4715)
    return (int(yr), int(mo), int(dy))


def _tzoffset(tz, t):
    """Returns the offset in seconds to GMT from a specific timezone (tz) at
    a specific time (t).  NB! The _tzoffset result is the same same sign as
    the time zone, i.e. GMT+2 has a 7200 second offset. This is the opposite
    sign of time.timezone which (confusingly) is -7200 for GMT+2."""
    try:
        return _TZINFO[tz].info(t)[0]
    except Exception:
        if numericTimeZoneMatch(tz) is not None:
            return int(tz[0:3]) * 3600 + int(tz[0] + tz[3:5]) * 60
        else:
            return 0  # ??


def _correctYear(year):
    # Y2K patch.
    if year >= 0 and year < 100:
        # 00-69 means 2000-2069, 70-99 means 1970-1999.
        if year < 70:
            year = 2000 + year
        else:
            year = 1900 + year
    return year


def safegmtime(t):
    '''gmtime with a safety zone.'''
    try:
        return gmtime(t)
    except (ValueError, OverflowError):
        raise TimeError('The time %f is beyond the range of this Python '
            'implementation.' % float(t))


def safelocaltime(t):
    '''localtime with a safety zone.'''
    try:
        return localtime(t)
    except (ValueError, OverflowError):
        raise TimeError('The time %f is beyond the range of this Python '
            'implementation.' % float(t))


def _tzoffset2rfc822zone(seconds):
    """Takes an offset, such as from _tzoffset(), and returns an rfc822
       compliant zone specification. Please note that the result of
       _tzoffset() is the negative of what time.localzone and time.altzone is.
    """
    return "%+03d%02d" % divmod((seconds // 60), 60)


def _tzoffset2iso8601zone(seconds):
    """Takes an offset, such as from _tzoffset(), and returns an ISO 8601
       compliant zone specification. Please note that the result of
       _tzoffset() is the negative of what time.localzone and time.altzone is.
    """
    return "%+03d:%02d" % divmod((seconds // 60), 60)


def Timezones():
    """Return the list of recognized timezone names"""
    return sorted(list(PytzCache._zmap.values()))


class strftimeFormatter(object):

    def __init__(self, dt, format):
        self.dt = dt
        self.format = format

    def __call__(self):
        return self.dt.strftime(self.format)


@implementer(IDateTime)
class DateTime(object):
    """DateTime objects represent instants in time and provide
       interfaces for controlling its representation without
       affecting the absolute value of the object.

       DateTime objects may be created from a wide variety of string
       or numeric data, or may be computed from other DateTime objects.
       DateTimes support the ability to convert their representations
       to many major timezones, as well as the ablility to create a
       DateTime object in the context of a given timezone.

       DateTime objects provide partial numerical behavior:

          - Two date-time objects can be subtracted to obtain a time,
            in days between the two.

          - A date-time object and a positive or negative number may
            be added to obtain a new date-time object that is the given
            number of days later than the input date-time object.

          - A positive or negative number and a date-time object may
            be added to obtain a new date-time object that is the given
            number of days later than the input date-time object.

          - A positive or negative number may be subtracted from a
            date-time object to obtain a new date-time object that is
            the given number of days earlier than the input date-time
            object.

        DateTime objects may be converted to integer, long, or float
        numbers of days since January 1, 1901, using the standard int,
        long, and float functions (Compatibility Note: int, long and
        float return the number of days since 1901 in GMT rather than
        local machine timezone). DateTime objects also provide access
        to their value in a float format usable with the python time
        module, provided that the value of the object falls in the
        range of the epoch-based time module, and as a datetime.datetime
        object.

        A DateTime object should be considered immutable; all conversion
        and numeric operations return a new DateTime object rather than
        modify the current object."""

    # For security machinery:
    __roles__ = None
    __allow_access_to_unprotected_subobjects__ = 1

    # Limit the amount of instance attributes
    __slots__ = (
        '_timezone_naive',
        '_tz',
        '_dayoffset',
        '_year',
        '_month',
        '_day',
        '_hour',
        '_minute',
        '_second',
        '_nearsec',
        '_d',
        '_micros',
        'time',
    )

    def __init__(self, *args, **kw):
        """Return a new date-time object"""
        try:
            return self._parse_args(*args, **kw)
        except (DateError, TimeError, DateTimeError):
            raise
        except Exception:
            raise SyntaxError('Unable to parse %s, %s' % (args, kw))

    def __getstate__(self):
        # We store a float of _micros, instead of the _micros long, as we most
        # often don't have any sub-second resolution and can save those bytes
        return (self._micros / 1000000.0,
            getattr(self, '_timezone_naive', False),
            self._tz)

    def __setstate__(self, value):
        if isinstance(value, tuple):
            self._parse_args(value[0], value[2])
            self._micros = long(value[0] * 1000000)
            self._timezone_naive = value[1]
        else:
            for k, v in value.items():
                if k in self.__slots__:
                    setattr(self, k, v)
            # BBB: support for very old DateTime pickles
            if '_micros' not in value:
                self._micros = long(value['_t'] * 1000000)
            if '_timezone_naive' not in value:
                self._timezone_naive = False

    def _parse_args(self, *args, **kw):
        """Return a new date-time object.

        A DateTime object always maintains its value as an absolute
        UTC time, and is represented in the context of some timezone
        based on the arguments used to create the object. A DateTime
        object's methods return values based on the timezone context.

        Note that in all cases the local machine timezone is used for
        representation if no timezone is specified.

        DateTimes may be created with from zero to seven arguments.

          - If the function is called with no arguments or with None,
            then the current date/time is returned, represented in the
            timezone of the local machine.

          - If the function is invoked with a single string argument
            which is a recognized timezone name, an object representing
            the current time is returned, represented in the specified
            timezone.

          - If the function is invoked with a single string argument
            representing a valid date/time, an object representing
            that date/time will be returned.

            As a general rule, any date-time representation that is
            recognized and unambigous to a resident of North America
            is acceptable. The reason for this qualification is that
            in North America, a date like: 2/1/1994 is interpreted
            as February 1, 1994, while in some parts of the world,
            it is interpreted as January 2, 1994.

            A date/time string consists of two components, a date
            component and an optional time component, separated by one
            or more spaces. If the time component is omited, 12:00am is
            assumed. Any recognized timezone name specified as the final
            element of the date/time string will be used for computing
            the date/time value. If you create a DateTime with the
            string 'Mar 9, 1997 1:45pm US/Pacific', the value will
            essentially be the same as if you had captured time.time()
            at the specified date and time on a machine in that timezone:

            <PRE>
            e=DateTime('US/Eastern')
            # returns current date/time, represented in US/Eastern.

            x=DateTime('1997/3/9 1:45pm')
            # returns specified time, represented in local machine zone.

            y=DateTime('Mar 9, 1997 13:45:00')
            # y is equal to x
            </PRE>

            The date component consists of year, month, and day
            values. The year value must be a one-, two-, or
            four-digit integer. If a one- or two-digit year is
            used, the year is assumed to be in the twentieth
            century. The month may be an integer, from 1 to 12, a
            month name, or a month abreviation, where a period may
            optionally follow the abreviation. The day must be an
            integer from 1 to the number of days in the month. The
            year, month, and day values may be separated by
            periods, hyphens, forward, shashes, or spaces. Extra
            spaces are permitted around the delimiters. Year,
            month, and day values may be given in any order as long
            as it is possible to distinguish the components. If all
            three components are numbers that are less than 13,
            then a a month-day-year ordering is assumed.

            The time component consists of hour, minute, and second
            values separated by colons.  The hour value must be an
            integer between 0 and 23 inclusively. The minute value
            must be an integer between 0 and 59 inclusively. The
            second value may be an integer value between 0 and
            59.999 inclusively. The second value or both the minute
            and second values may be ommitted. The time may be
            followed by am or pm in upper or lower case, in which
            case a 12-hour clock is assumed.

            New in Zope 2.4:
            The DateTime constructor automatically detects and handles
            ISO8601 compliant dates (YYYY-MM-DDThh:ss:mmTZD).

            New in Zope 2.9.6:
            The existing ISO8601 parser was extended to support almost
            the whole ISO8601 specification. New formats includes:

            <PRE>
            y=DateTime('1993-045')
            # returns the 45th day from 1993, which is 14th February

            w=DateTime('1993-W06-7')
            # returns the 7th day from the 6th week from 1993, which
            # is also 14th February
            </PRE>

            See http://en.wikipedia.org/wiki/ISO_8601 for full specs.

            Note that the Zope DateTime parser assumes timezone naive ISO
            strings to be in UTC rather than local time as specified.

          - If the DateTime function is invoked with a single Numeric
            argument, the number is assumed to be a floating point value
            such as that returned by time.time().

            A DateTime object is returned that represents the GMT value
            of the time.time() float represented in the local machine's
            timezone.

          - If the DateTime function is invoked with a single argument
            that is a DateTime instane, a copy of the passed object will
            be created.

          - New in 2.11:
            The DateTime function may now be invoked with a single argument
            that is a datetime.datetime instance. DateTimes may be converted
            back to datetime.datetime objects with asdatetime().
            DateTime instances may be converted to a timezone naive
            datetime.datetime in UTC with utcdatetime().

          - If the function is invoked with two numeric arguments, then
            the first is taken to be an integer year and the second
            argument is taken to be an offset in days from the beginning
            of the year, in the context of the local machine timezone.

            The date-time value returned is the given offset number of
            days from the beginning of the given year, represented in
            the timezone of the local machine. The offset may be positive
            or negative.

            Two-digit years are assumed to be in the twentieth
            century.

          - If the function is invoked with two arguments, the first
            a float representing a number of seconds past the epoch
            in gmt (such as those returned by time.time()) and the
            second a string naming a recognized timezone, a DateTime
            with a value of that gmt time will be returned, represented
            in the given timezone.

            <PRE>
            import time
            t=time.time()

            now_east=DateTime(t,'US/Eastern')
            # Time t represented as US/Eastern

            now_west=DateTime(t,'US/Pacific')
            # Time t represented as US/Pacific

            # now_east == now_west
            # only their representations are different
            </PRE>

          - If the function is invoked with three or more numeric
            arguments, then the first is taken to be an integer
            year, the second is taken to be an integer month, and
            the third is taken to be an integer day. If the
            combination of values is not valid, then a
            DateError is raised. Two-digit years are assumed
            to be in the twentieth century. The fourth, fifth, and
            sixth arguments specify a time in hours, minutes, and
            seconds; hours and minutes should be positive integers
            and seconds is a positive floating point value, all of
            these default to zero if not given. An optional string may
            be given as the final argument to indicate timezone (the
            effect of this is as if you had taken the value of time.time()
            at that time on a machine in the specified timezone).

            New in Zope 2.7:
            A new keyword parameter "datefmt" can be passed to the
            constructor. If set to "international", the constructor
            is forced to treat ambigious dates as "days before month
            before year". This useful if you need to parse non-US
            dates in a reliable way

        In any case that a floating point number of seconds is given
        or derived, it's rounded to the nearest millisecond.

        If a string argument passed to the DateTime constructor cannot be
        parsed, it will raise DateTime.SyntaxError. Invalid date components
        will raise a DateError, while invalid time or timezone components
        will raise a DateTimeError.

        The module function Timezones() will return a list of the (common)
        timezones recognized by the DateTime module. Recognition of
        timezone names is case-insensitive.
        """

        datefmt = kw.get('datefmt', getDefaultDateFormat())
        d = t = s = None
        ac = len(args)
        microsecs = None

        if ac == 10:
            # Internal format called only by DateTime
            yr, mo, dy, hr, mn, sc, tz, t, d, s = args
        elif ac == 11:
            # Internal format that includes milliseconds (from the epoch)
            yr, mo, dy, hr, mn, sc, tz, t, d, s, millisecs = args
            microsecs = millisecs * 1000

        elif ac == 12:
            # Internal format that includes microseconds (from the epoch) and a
            # flag indicating whether this was constructed in a timezone naive
            # manner
            yr, mo, dy, hr, mn, sc, tz, t, d, s, microsecs, tznaive = args
            if tznaive is not None:  # preserve this information
                self._timezone_naive = tznaive

        elif not args or (ac and args[0] is None):
            # Current time, to be displayed in local timezone
            t = time()
            lt = safelocaltime(t)
            tz = self.localZone(lt)
            ms = (t - math.floor(t))
            s, d = _calcSD(t)
            yr, mo, dy, hr, mn, sc = lt[:6]
            sc = sc + ms
            self._timezone_naive = False

        elif ac == 1:
            arg = args[0]

            if arg == '':
                raise SyntaxError(arg)

            if isinstance(arg, DateTime):
                """Construct a new DateTime instance from a given
                DateTime instance.
                """
                t = arg.timeTime()
                s, d = _calcSD(t)
                yr, mo, dy, hr, mn, sc, tz = arg.parts()

            elif isinstance(arg, datetime):
                yr, mo, dy, hr, mn, sc, numerictz, tznaive = \
                    self._parse_iso8601_preserving_tznaive(arg.isoformat())
                if arg.tzinfo is None:
                    self._timezone_naive = True
                    tz = None
                else:
                    self._timezone_naive = False
                    # if we have a pytz tzinfo, use the `zone` attribute
                    # as a key
                    tz = getattr(arg.tzinfo, 'zone', numerictz)
                ms = sc - math.floor(sc)
                x = _calcDependentSecond2(yr, mo, dy, hr, mn, sc)

                if tz:
                    try:
                        zone = _TZINFO[tz]
                    except DateTimeError:
                        try:
                            zone = _TZINFO[numerictz]
                        except DateTimeError:
                            raise DateTimeError(
                                'Unknown time zone in date: %s' % arg)
                    tz = zone.tzinfo.zone
                else:
                    tz = self._calcTimezoneName(x, ms)
                s, d, t, microsecs = _calcIndependentSecondEtc(tz, x, ms)

            elif (isinstance(arg, basestring) and
                  arg.lower() in _TZINFO._zidx):
                # Current time, to be displayed in specified timezone
                t, tz = time(), _TZINFO._zmap[arg.lower()]
                ms = (t - math.floor(t))
                # Use integer arithmetic as much as possible.
                s, d = _calcSD(t)
                x = _calcDependentSecond(tz, t)
                yr, mo, dy, hr, mn, sc = _calcYMDHMS(x, ms)

            elif isinstance(arg, basestring):
                # Date/time string
                iso8601 = iso8601Match(arg.strip())
                fields_iso8601 = iso8601 and iso8601.groupdict() or {}
                if fields_iso8601 and not fields_iso8601.get('garbage'):
                    yr, mo, dy, hr, mn, sc, tz, tznaive = \
                        self._parse_iso8601_preserving_tznaive(arg)
                    self._timezone_naive = tznaive
                else:
                    yr, mo, dy, hr, mn, sc, tz = self._parse(arg, datefmt)

                if not self._validDate(yr, mo, dy):
                    raise DateError('Invalid date: %s' % arg)
                if not self._validTime(hr, mn, int(sc)):
                    raise TimeError('Invalid time: %s' % arg)
                ms = sc - math.floor(sc)
                x = _calcDependentSecond2(yr, mo, dy, hr, mn, sc)

                if tz:
                    try:
                        tz = _TZINFO._zmap[tz.lower()]
                    except KeyError:
                        if numericTimeZoneMatch(tz) is None:
                            raise DateTimeError(
                                'Unknown time zone in date: %s' % arg)
                else:
                    tz = self._calcTimezoneName(x, ms)
                s, d, t, microsecs = _calcIndependentSecondEtc(tz, x, ms)

            else:
                # Seconds from epoch, gmt
                t = arg
                lt = safelocaltime(t)
                tz = self.localZone(lt)
                ms = (t - math.floor(t))
                s, d = _calcSD(t)
                yr, mo, dy, hr, mn, sc = lt[:6]
                sc = sc + ms

        elif ac == 2:
            if isinstance(args[1], basestring):
                # Seconds from epoch (gmt) and timezone
                t, tz = args
                ms = (t - math.floor(t))
                try:
                    tz = _TZINFO._zmap[tz.lower()]
                except KeyError:
                    if numericTimeZoneMatch(tz) is None:
                        raise DateTimeError('Unknown time zone: %s' % tz)
                # Use integer arithmetic as much as possible.
                s, d = _calcSD(t)
                x = _calcDependentSecond(tz, t)
                yr, mo, dy, hr, mn, sc = _calcYMDHMS(x, ms)
            else:
                # Year, julian expressed in local zone
                t = time()
                lt = safelocaltime(t)
                tz = self.localZone(lt)
                yr, jul = args
                yr = _correctYear(yr)
                d = (_julianday(yr, 1, 0) - jd1901) + jul
                x_float = d * 86400.0
                x_floor = math.floor(x_float)
                ms = x_float - x_floor
                x = long(x_floor)
                yr, mo, dy, hr, mn, sc = _calcYMDHMS(x, ms)
                s, d, t, microsecs = _calcIndependentSecondEtc(tz, x, ms)
        else:
            # Explicit format
            yr, mo, dy = args[:3]
            hr, mn, sc, tz = 0, 0, 0, 0
            yr = _correctYear(yr)
            if not self._validDate(yr, mo, dy):
                raise DateError('Invalid date: %s' % (args, ))
            args = args[3:]
            if args:
                hr, args = args[0], args[1:]
                if args:
                    mn, args = args[0], args[1:]
                    if args:
                        sc, args = args[0], args[1:]
                        if args:
                            tz, args = args[0], args[1:]
                            if args:
                                raise DateTimeError('Too many arguments')
            if not self._validTime(hr, mn, sc):
                raise TimeError('Invalid time: %s' % repr(args))

            x = _calcDependentSecond2(yr, mo, dy, hr, mn, sc)
            ms = sc - math.floor(sc)
            if tz:
                try:
                    tz = _TZINFO._zmap[tz.lower()]
                except KeyError:
                    if numericTimeZoneMatch(tz) is None:
                        raise DateTimeError('Unknown time zone: %s' % tz)
            else:
                # Get local time zone name
                tz = self._calcTimezoneName(x, ms)
            s, d, t, microsecs = _calcIndependentSecondEtc(tz, x, ms)

        self._dayoffset = int((_julianday(yr, mo, dy) + 2) % 7)
        # Round to nearest microsecond in platform-independent way.  You
        # cannot rely on C sprintf (Python '%') formatting to round
        # consistently; doing it ourselves ensures that all but truly
        # horrid C sprintf implementations will yield the same result
        # x-platform, provided the format asks for exactly 6 digits after
        # the decimal point.
        sc = round(sc, 6)
        if sc >= 60.0:  # can happen if, e.g., orig sc was 59.9999999
            sc = 59.999999
        self._nearsec = math.floor(sc)
        self._year, self._month, self._day = yr, mo, dy
        self._hour, self._minute, self._second = hr, mn, sc
        self.time, self._d, self._tz = s, d, tz
        # self._micros is the time since the epoch
        # in long integer microseconds.
        if microsecs is None:
            microsecs = long(math.floor(t * 1000000.0))
        self._micros = microsecs

    def localZone(self, ltm=None):
        '''Returns the time zone on the given date.  The time zone
        can change according to daylight savings.'''
        if not _multipleZones:
            return _localzone0
        if ltm is None:
            ltm = localtime(time())
        isDST = ltm[8]
        lz = isDST and _localzone1 or _localzone0
        return lz

    def _calcTimezoneName(self, x, ms):
        # Derive the name of the local time zone at the given
        # timezone-dependent second.
        if not _multipleZones:
            return _localzone0
        fsetAtEpoch = _tzoffset(_localzone0, 0.0)
        nearTime = x - fsetAtEpoch - long(EPOCH) + 86400 + ms
        # nearTime is within an hour of being correct.
        try:
            ltm = safelocaltime(nearTime)
        except:
            # We are beyond the range of Python's date support.
            # Hopefully we can assume that daylight savings schedules
            # repeat every 28 years.  Calculate the name of the
            # time zone using a supported range of years.
            yr, mo, dy, hr, mn, sc = _calcYMDHMS(x, 0)
            yr = ((yr - 1970) % 28) + 1970
            x = _calcDependentSecond2(yr, mo, dy, hr, mn, sc)
            nearTime = x - fsetAtEpoch - long(EPOCH) + 86400 + ms

            # nearTime might still be negative if we are east of Greenwich.
            # But we can asume on 1969/12/31 were no timezone changes.
            nearTime = max(0, nearTime)

            ltm = safelocaltime(nearTime)
        tz = self.localZone(ltm)
        return tz

    def _parse(self, st, datefmt=getDefaultDateFormat()):
        # Parse date-time components from a string
        month = year = tz = tm = None
        ValidZones = _TZINFO._zidx
        TimeModifiers = ['am', 'pm']

        # Find timezone first, since it should always be the last
        # element, and may contain a slash, confusing the parser.
        st = st.strip()
        sp = st.split()
        tz = sp[-1]
        if tz and (tz.lower() in ValidZones):
            self._timezone_naive = False
            st = ' '.join(sp[:-1])
        else:
            self._timezone_naive = True
            tz = None  # Decide later, since the default time zone
        # could depend on the date.

        ints = []
        i = 0
        l = len(st)
        while i < l:
            while i < l and st[i] in SPACE_CHARS:
                i += 1
            if i < l and st[i] in DELIMITERS:
                d = st[i]
                i += 1
            else:
                d = ''
            while i < l and st[i] in SPACE_CHARS:
                i += 1

            # The float pattern needs to look back 1 character, because it
            # actually looks for a preceding colon like ':33.33'. This is
            # needed to avoid accidentally matching the date part of a
            # dot-separated date string such as '1999.12.31'.
            if i > 0:
                b = i - 1
            else:
                b = i

            ts_results = FLT_PATTERN.match(st, b)
            if ts_results:
                s = ts_results.group(1)
                i = i + len(s)
                ints.append(float(s))
                continue

            #AJ
            ts_results = INT_PATTERN.match(st, i)
            if ts_results:
                s = ts_results.group(0)

                ls = len(s)
                i = i + ls
                if (ls == 4 and d and d in '+-' and
                   (len(ints) + (not not month) >= 3)):
                    tz = '%s%s' % (d, s)
                else:
                    v = int(s)
                    ints.append(v)
                continue

            ts_results = NAME_PATTERN.match(st, i)
            if ts_results:
                s = ts_results.group(0).lower()
                i = i + len(s)
                if i < l and st[i] == '.':
                    i += 1
                # Check for month name:
                _v = _MONTHMAP.get(s)
                if _v is not None:
                    if month is None:
                        month = _v
                    else:
                        raise SyntaxError(st)
                    continue
                # Check for time modifier:
                if s in TimeModifiers:
                    if tm is None:
                        tm = s
                    else:
                        raise SyntaxError(st)
                    continue
                # Check for and skip day of week:
                if s in _DAYMAP:
                    continue

            raise SyntaxError(st)

        day = None
        if ints[-1] > 60 and d not in ('.', ':', '/') and len(ints) > 2:
            year = ints[-1]
            del ints[-1]
            if month:
                day = ints[0]
                del ints[:1]
            else:
                if datefmt == "us":
                    month = ints[0]
                    day = ints[1]
                else:
                    month = ints[1]
                    day = ints[0]
                del ints[:2]
        elif month:
            if len(ints) > 1:
                if ints[0] > 31:
                    year = ints[0]
                    day = ints[1]
                else:
                    year = ints[1]
                    day = ints[0]
                del ints[:2]
        elif len(ints) > 2:
            if ints[0] > 31:
                year = ints[0]
                if ints[1] > 12:
                    day = ints[1]
                    month = ints[2]
                else:
                    day = ints[2]
                    month = ints[1]
            if ints[1] > 31:
                year = ints[1]
                if ints[0] > 12 and ints[2] <= 12:
                    day = ints[0]
                    month = ints[2]
                elif ints[2] > 12 and ints[0] <= 12:
                    day = ints[2]
                    month = ints[0]
            elif ints[2] > 31:
                year = ints[2]
                if ints[0] > 12:
                    day = ints[0]
                    month = ints[1]
                else:
                    if datefmt == "us":
                        day = ints[1]
                        month = ints[0]
                    else:
                        day = ints[0]
                        month = ints[1]

            elif ints[0] <= 12:
                month = ints[0]
                day = ints[1]
                year = ints[2]
            del ints[:3]

        if day is None:
            # Use today's date.
            year, month, day = localtime(time())[:3]

        year = _correctYear(year)
        if year < 1000:
            raise SyntaxError(st)

        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        try:
            if not day or day > _MONTH_LEN[leap][month]:
                raise DateError(st)
        except IndexError:
            raise DateError(st)

        tod = 0
        if ints:
            i = ints[0]
            # Modify hour to reflect am/pm
            if tm and (tm == 'pm') and i < 12:
                i += 12
            if tm and (tm == 'am') and i == 12:
                i = 0
            if i > 24:
                raise TimeError(st)
            tod = tod + int(i) * 3600
            del ints[0]
            if ints:
                i = ints[0]
                if i > 60:
                    raise TimeError(st)
                tod = tod + int(i) * 60
                del ints[0]
                if ints:
                    i = ints[0]
                    if i > 60:
                        raise TimeError(st)
                    tod = tod + i
                    del ints[0]
                    if ints:
                        raise SyntaxError(st)

        tod_int = int(math.floor(tod))
        ms = tod - tod_int
        hr, mn, sc = _calcHMS(tod_int, ms)
        if not tz:
            # Figure out what time zone it is in the local area
            # on the given date.
            x = _calcDependentSecond2(year, month, day, hr, mn, sc)
            tz = self._calcTimezoneName(x, ms)

        return year, month, day, hr, mn, sc, tz

    # Internal methods
    def _validDate(self, y, m, d):
        if m < 1 or m > 12 or y < 0 or d < 1 or d > 31:
            return 0
        return d <= _MONTH_LEN[
            (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))][m]

    def _validTime(self, h, m, s):
        return h >= 0 and h <= 23 and m >= 0 and m <= 59 and s >= 0 and s < 60

    def __getattr__(self, name):
        if '%' in name:
            return strftimeFormatter(self, name)
        raise AttributeError(name)

    # Conversion and comparison methods

    def timeTime(self):
        """Return the date/time as a floating-point number in UTC,
        in the format used by the python time module.

        Note that it is possible to create date/time values with
        DateTime that have no meaningful value to the time module.
        """
        return self._micros / 1000000.0

    def toZone(self, z):
        """Return a DateTime with the value as the current
        object, represented in the indicated timezone.
        """
        t, tz = self._t, _TZINFO._zmap[z.lower()]
        micros = self.micros()
        tznaive = False  # you're performing a timzone change, can't be naive

        try:
            # Try to use time module for speed.
            yr, mo, dy, hr, mn, sc = safegmtime(t + _tzoffset(tz, t))[:6]
            sc = self._second
            return self.__class__(yr, mo, dy, hr, mn, sc, tz, t,
                                  self._d, self.time, micros, tznaive)
        except Exception:
            # gmtime can't perform the calculation in the given range.
            # Calculate the difference between the two time zones.
            tzdiff = _tzoffset(tz, t) - _tzoffset(self._tz, t)
            if tzdiff == 0:
                return self
            sc = self._second
            ms = sc - math.floor(sc)
            x = _calcDependentSecond2(self._year, self._month, self._day,
                                      self._hour, self._minute, sc)
            x_new = x + tzdiff
            yr, mo, dy, hr, mn, sc = _calcYMDHMS(x_new, ms)
            return self.__class__(yr, mo, dy, hr, mn, sc, tz, t,
                                  self._d, self.time, micros, tznaive)

    def isFuture(self):
        """Return true if this object represents a date/time
        later than the time of the call.
        """
        return (self._t > time())

    def isPast(self):
        """Return true if this object represents a date/time
        earlier than the time of the call.
        """
        return (self._t < time())

    def isCurrentYear(self):
        """Return true if this object represents a date/time
        that falls within the current year, in the context
        of this object\'s timezone representation.
        """
        t = time()
        return safegmtime(t + _tzoffset(self._tz, t))[0] == self._year

    def isCurrentMonth(self):
        """Return true if this object represents a date/time
        that falls within the current month, in the context
        of this object\'s timezone representation.
        """
        t = time()
        gmt = safegmtime(t + _tzoffset(self._tz, t))
        return gmt[0] == self._year and gmt[1] == self._month

    def isCurrentDay(self):
        """Return true if this object represents a date/time
        that falls within the current day, in the context
        of this object\'s timezone representation.
        """
        t = time()
        gmt = safegmtime(t + _tzoffset(self._tz, t))
        return (gmt[0] == self._year and gmt[1] == self._month and
                gmt[2] == self._day)

    def isCurrentHour(self):
        """Return true if this object represents a date/time
        that falls within the current hour, in the context
        of this object\'s timezone representation.
        """
        t = time()
        gmt = safegmtime(t + _tzoffset(self._tz, t))
        return (gmt[0] == self._year and gmt[1] == self._month and
                gmt[2] == self._day and gmt[3] == self._hour)

    def isCurrentMinute(self):
        """Return true if this object represents a date/time
        that falls within the current minute, in the context
        of this object\'s timezone representation.
        """
        t = time()
        gmt = safegmtime(t + _tzoffset(self._tz, t))
        return (gmt[0] == self._year and gmt[1] == self._month and
                gmt[2] == self._day and gmt[3] == self._hour and
                gmt[4] == self._minute)

    def earliestTime(self):
        """Return a new DateTime object that represents the earliest
        possible time (in whole seconds) that still falls within
        the current object\'s day, in the object\'s timezone context.
        """
        return self.__class__(
            self._year, self._month, self._day, 0, 0, 0, self._tz)

    def latestTime(self):
        """Return a new DateTime object that represents the latest
        possible time (in whole seconds) that still falls within
        the current object\'s day, in the object\'s timezone context.
        """
        return self.__class__(
            self._year, self._month, self._day, 23, 59, 59, self._tz)

    def greaterThan(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the python time module.

        Returns true if the object represents a date/time greater
        than the specified DateTime or time module style time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        if t is None:
            t = 0
        if isinstance(t, float):
            return self._micros > long(t * 1000000)
        try:
            return self._micros > t._micros
        except AttributeError:
            return self._micros > t

    __gt__ = greaterThan

    def greaterThanEqualTo(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the python time module.

        Returns true if the object represents a date/time greater
        than or equal to the specified DateTime or time module style
        time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        if t is None:
            t = 0
        if isinstance(t, float):
            return self._micros >= long(t * 1000000)
        try:
            return self._micros >= t._micros
        except AttributeError:
            return self._micros >= t

    __ge__ = greaterThanEqualTo

    def equalTo(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the python time module.

        Returns true if the object represents a date/time equal to
        the specified DateTime or time module style time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        if t is None:
            t = 0
        if isinstance(t, float):
            return self._micros == long(t * 1000000)
        try:
            return self._micros == t._micros
        except AttributeError:
            return self._micros == t

    def notEqualTo(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the python time module.

        Returns true if the object represents a date/time not equal
        to the specified DateTime or time module style time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        return not self.equalTo(t)

    def __eq__(self, t):
        """Compare this DateTime object to another DateTime object.
        Return True if their internal state is the same. Two objects
        representing the same time in different timezones are regared as
        unequal. Use the equalTo method if you are only interested in them
        refering to the same moment in time.
        """
        if not isinstance(t, DateTime):
            return False
        return (self._micros, self._tz) == (t._micros, t._tz)

    def __ne__(self, t):
        return not self.__eq__(t)

    def lessThan(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the python time module.

        Returns true if the object represents a date/time less than
        the specified DateTime or time module style time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        if t is None:
            t = 0
        if isinstance(t, float):
            return self._micros < long(t * 1000000)
        try:
            return self._micros < t._micros
        except AttributeError:
            return self._micros < t

    __lt__ = lessThan

    def lessThanEqualTo(self, t):
        """Compare this DateTime object to another DateTime object
        OR a floating point number such as that which is returned
        by the python time module.

        Returns true if the object represents a date/time less than
        or equal to the specified DateTime or time module style time.

        Revised to give more correct results through comparison of
        long integer microseconds.
        """
        if t is None:
            t = 0
        if isinstance(t, float):
            return self._micros <= long(t * 1000000)
        try:
            return self._micros <= t._micros
        except AttributeError:
            return self._micros <= t

    __le__ = lessThanEqualTo

    def isLeapYear(self):
        """Return true if the current year (in the context of the
        object\'s timezone) is a leap year.
        """
        return (self._year % 4 == 0 and
            (self._year % 100 != 0 or self._year % 400 == 0))

    def dayOfYear(self):
        """Return the day of the year, in context of the timezone
        representation of the object.
        """
        d = int(self._d + (_tzoffset(self._tz, self._t) / 86400.0))
        return int((d + jd1901) - _julianday(self._year, 1, 0))

    # Component access
    def parts(self):
        """Return a tuple containing the calendar year, month,
        day, hour, minute second and timezone of the object.
        """
        return (self._year, self._month, self._day, self._hour,
                self._minute, self._second, self._tz)

    def timezone(self):
        """Return the timezone in which the object is represented."""
        return self._tz

    def tzoffset(self):
        """Return the timezone offset for the objects timezone."""
        return _tzoffset(self._tz, self._t)

    def year(self):
        """Return the calendar year of the object."""
        return self._year

    def month(self):
        """Return the month of the object as an integer."""
        return self._month

    @property
    def _fmon(self):
        return _MONTHS[self._month]

    def Month(self):
        """Return the full month name."""
        return self._fmon

    @property
    def _amon(self):
        return _MONTHS_A[self._month]

    def aMonth(self):
        """Return the abreviated month name."""
        return self._amon

    def Mon(self):
        """Compatibility: see aMonth."""
        return self._amon

    @property
    def _pmon(self):
        return _MONTHS_P[self._month]

    def pMonth(self):
        """Return the abreviated (with period) month name."""
        return self._pmon

    def Mon_(self):
        """Compatibility: see pMonth."""
        return self._pmon

    def day(self):
        """Return the integer day."""
        return self._day

    @property
    def _fday(self):
        return _DAYS[self._dayoffset]

    def Day(self):
        """Return the full name of the day of the week."""
        return self._fday

    def DayOfWeek(self):
        """Compatibility: see Day."""
        return self._fday

    @property
    def _aday(self):
        return _DAYS_A[self._dayoffset]

    def aDay(self):
        """Return the abreviated name of the day of the week."""
        return self._aday

    @property
    def _pday(self):
        return _DAYS_P[self._dayoffset]

    def pDay(self):
        """Return the abreviated (with period) name of the day of the week."""
        return self._pday

    def Day_(self):
        """Compatibility: see pDay."""
        return self._pday

    def dow(self):
        """Return the integer day of the week, where sunday is 0."""
        return self._dayoffset

    def dow_1(self):
        """Return the integer day of the week, where sunday is 1."""
        return self._dayoffset + 1

    @property
    def _pmhour(self):
        hr = self._hour
        if hr > 12:
            return hr - 12
        return hr or 12

    def h_12(self):
        """Return the 12-hour clock representation of the hour."""
        return self._pmhour

    def h_24(self):
        """Return the 24-hour clock representation of the hour."""
        return self._hour

    @property
    def _pm(self):
        hr = self._hour
        if hr >= 12:
            return 'pm'
        return 'am'

    def ampm(self):
        """Return the appropriate time modifier (am or pm)."""
        return self._pm

    def hour(self):
        """Return the 24-hour clock representation of the hour."""
        return self._hour

    def minute(self):
        """Return the minute."""
        return self._minute

    def second(self):
        """Return the second."""
        return self._second

    def millis(self):
        """Return the millisecond since the epoch in GMT."""
        return self._micros // 1000

    def micros(self):
        """Return the microsecond since the epoch in GMT."""
        return self._micros

    def timezoneNaive(self):
        """The python datetime module introduces the idea of distinguishing
        between timezone aware and timezone naive datetime values. For lossless
        conversion to and from datetime.datetime record if we record this
        information using True / False. DateTime makes no distinction, when we
        don't have any information we return None here.
        """
        try:
            return self._timezone_naive
        except AttributeError:
            return None

    def strftime(self, format):
        """Format the date/time using the *current timezone representation*."""
        x = _calcDependentSecond2(self._year, self._month, self._day,
                                  self._hour, self._minute, self._second)
        ltz = self._calcTimezoneName(x, 0)
        tzdiff = _tzoffset(ltz, self._t) - _tzoffset(self._tz, self._t)
        zself = self + tzdiff / 86400.0
        microseconds = int((zself._second - zself._nearsec) * 1000000)
        unicode_format = False
        if isinstance(format, explicit_unicode_type):
            format = format.encode('utf-8')
            unicode_format = True
        ds = datetime(zself._year, zself._month, zself._day, zself._hour,
               zself._minute, int(zself._nearsec),
               microseconds).strftime(format)
        if unicode_format:
            return ds.decode('utf-8')
        return ds

    # General formats from previous DateTime
    def Date(self):
        """Return the date string for the object."""
        return "%s/%2.2d/%2.2d" % (self._year, self._month, self._day)

    def Time(self):
        """Return the time string for an object to the nearest second."""
        return '%2.2d:%2.2d:%2.2d' % (self._hour, self._minute, self._nearsec)

    def TimeMinutes(self):
        """Return the time string for an object not showing seconds."""
        return '%2.2d:%2.2d' % (self._hour, self._minute)

    def AMPM(self):
        """Return the time string for an object to the nearest second."""
        return '%2.2d:%2.2d:%2.2d %s' % (
            self._pmhour, self._minute, self._nearsec, self._pm)

    def AMPMMinutes(self):
        """Return the time string for an object not showing seconds."""
        return '%2.2d:%2.2d %s' % (self._pmhour, self._minute, self._pm)

    def PreciseTime(self):
        """Return the time string for the object."""
        return '%2.2d:%2.2d:%06.3f' % (self._hour, self._minute, self._second)

    def PreciseAMPM(self):
        """Return the time string for the object."""
        return '%2.2d:%2.2d:%06.3f %s' % (
            self._pmhour, self._minute, self._second, self._pm)

    def yy(self):
        """Return calendar year as a 2 digit string."""
        return str(self._year)[-2:]

    def mm(self):
        """Return month as a 2 digit string."""
        return '%02d' % self._month

    def dd(self):
        """Return day as a 2 digit string."""
        return '%02d' % self._day

    def rfc822(self):
        """Return the date in RFC 822 format."""
        tzoffset = _tzoffset2rfc822zone(_tzoffset(self._tz, self._t))
        return '%s, %2.2d %s %d %2.2d:%2.2d:%2.2d %s' % (
            self._aday, self._day, self._amon, self._year,
            self._hour, self._minute, self._nearsec, tzoffset)

    # New formats
    def fCommon(self):
        """Return a string representing the object\'s value
        in the format: March 1, 1997 1:45 pm.
        """
        return '%s %s, %4.4d %s:%2.2d %s' % (
               self._fmon, self._day, self._year, self._pmhour,
               self._minute, self._pm)

    def fCommonZ(self):
        """Return a string representing the object\'s value
        in the format: March 1, 1997 1:45 pm US/Eastern.
        """
        return '%s %s, %4.4d %d:%2.2d %s %s' % (
               self._fmon, self._day, self._year, self._pmhour,
               self._minute, self._pm, self._tz)

    def aCommon(self):
        """Return a string representing the object\'s value
        in the format: Mar 1, 1997 1:45 pm.
        """
        return '%s %s, %4.4d %s:%2.2d %s' % (
               self._amon, self._day, self._year, self._pmhour,
               self._minute, self._pm)

    def aCommonZ(self):
        """Return a string representing the object\'s value
        in the format: Mar 1, 1997 1:45 pm US/Eastern.
        """
        return '%s %s, %4.4d %d:%2.2d %s %s' % (
               self._amon, self._day, self._year, self._pmhour,
               self._minute, self._pm, self._tz)

    def pCommon(self):
        """Return a string representing the object\'s value
        in the format: Mar. 1, 1997 1:45 pm.
        """
        return '%s %s, %4.4d %s:%2.2d %s' % (
               self._pmon, self._day, self._year, self._pmhour,
               self._minute, self._pm)

    def pCommonZ(self):
        """Return a string representing the object\'s value
        in the format: Mar. 1, 1997 1:45 pm US/Eastern.
        """
        return '%s %s, %4.4d %d:%2.2d %s %s' % (
               self._pmon, self._day, self._year, self._pmhour,
               self._minute, self._pm, self._tz)

    def ISO(self):
        """Return the object in ISO standard format.

        Note: this is *not* ISO 8601-format! See the ISO8601 and
        HTML4 methods below for ISO 8601-compliant output.

        Dates are output as: YYYY-MM-DD HH:MM:SS
        """
        return "%.4d-%.2d-%.2d %.2d:%.2d:%.2d" % (
            self._year, self._month, self._day,
            self._hour, self._minute, self._second)

    def ISO8601(self):
        """Return the object in ISO 8601-compatible format containing the
        date, time with seconds-precision and the time zone identifier.

        See: http://www.w3.org/TR/NOTE-datetime

        Dates are output as: YYYY-MM-DDTHH:MM:SSTZD
            T is a literal character.
            TZD is Time Zone Designator, format +HH:MM or -HH:MM

        If the instance is timezone naive (it was not specified with a timezone
        when it was constructed) then the timezone is ommitted.

        The HTML4 method below offers the same formatting, but converts
        to UTC before returning the value and sets the TZD "Z".
        """
        if self.timezoneNaive():
            return "%0.4d-%0.2d-%0.2dT%0.2d:%0.2d:%0.2d" % (
                self._year, self._month, self._day,
                self._hour, self._minute, self._second)
        tzoffset = _tzoffset2iso8601zone(_tzoffset(self._tz, self._t))
        return "%0.4d-%0.2d-%0.2dT%0.2d:%0.2d:%0.2d%s" % (
            self._year, self._month, self._day,
            self._hour, self._minute, self._second, tzoffset)

    def HTML4(self):
        """Return the object in the format used in the HTML4.0 specification,
        one of the standard forms in ISO8601.

        See: http://www.w3.org/TR/NOTE-datetime

        Dates are output as: YYYY-MM-DDTHH:MM:SSZ
           T, Z are literal characters.
           The time is in UTC.
        """
        newdate = self.toZone('UTC')
        return "%0.4d-%0.2d-%0.2dT%0.2d:%0.2d:%0.2dZ" % (
            newdate._year, newdate._month, newdate._day,
            newdate._hour, newdate._minute, newdate._second)

    def asdatetime(self):
        """Return a standard libary datetime.datetime
        """
        tznaive = self.timezoneNaive()
        if tznaive:
            tzinfo = None
        else:
            tzinfo = _TZINFO[self._tz].tzinfo
        second = int(self._second)
        microsec = self.micros() % 1000000
        dt = datetime(self._year, self._month, self._day, self._hour,
                      self._minute, second, microsec, tzinfo)
        return dt

    def utcdatetime(self):
        """Convert the time to UTC then return a timezone naive datetime object
        """
        utc = self.toZone('UTC')
        second = int(utc._second)
        microsec = utc.micros() % 1000000
        dt = datetime(utc._year, utc._month, utc._day, utc._hour,
                      utc._minute, second, microsec)
        return dt

    def __add__(self, other):
        """A DateTime may be added to a number and a number may be
        added to a DateTime;  two DateTimes cannot be added.
        """
        if hasattr(other, '_t'):
            raise DateTimeError('Cannot add two DateTimes')
        o = float(other)
        tz = self._tz
        omicros = round(o * 86400000000)
        tmicros = self.micros() + omicros
        t = tmicros / 1000000.0
        d = (tmicros + long(EPOCH * 1000000)) / 86400000000.0
        s = d - math.floor(d)
        ms = t - math.floor(t)
        x = _calcDependentSecond(tz, t)
        yr, mo, dy, hr, mn, sc = _calcYMDHMS(x, ms)
        return self.__class__(yr, mo, dy, hr, mn, sc, self._tz,
            t, d, s, None, self.timezoneNaive())

    __radd__ = __add__

    def __sub__(self, other):
        """Either a DateTime or a number may be subtracted from a
        DateTime, however, a DateTime may not be subtracted from
        a number.
        """
        if hasattr(other, '_d'):
            return (self.micros() - other.micros()) / 86400000000.0
        else:
            return self.__add__(-(other))

    def __repr__(self):
        """Convert a DateTime to a string that looks like a Python
        expression.
        """
        return '%s(\'%s\')' % (self.__class__.__name__, str(self))

    def __str__(self):
        """Convert a DateTime to a string."""
        y, m, d = self._year, self._month, self._day
        h, mn, s, t = self._hour, self._minute, self._second, self._tz
        if s == int(s):
            # A whole number of seconds -- suppress milliseconds.
            return '%4.4d/%2.2d/%2.2d %2.2d:%2.2d:%2.2d %s' % (
                y, m, d, h, mn, s, t)
        else:
            # s is already rounded to the nearest microsecond, and
            # it's not a whole number of seconds.  Be sure to print
            # 2 digits before the decimal point.
            return '%4.4d/%2.2d/%2.2d %2.2d:%2.2d:%06.6f %s' % (
                y, m, d, h, mn, s, t)

    def __hash__(self):
        """Compute a hash value for a DateTime."""
        return int(((self._year % 100 * 12 + self._month) * 31 +
                    self._day + self.time) * 100)

    def __int__(self):
        """Convert to an integer number of seconds since the epoch (gmt)."""
        return int(self.micros() // 1000000)

    def __long__(self):
        """Convert to a long-int number of seconds since the epoch (gmt)."""
        return long(self.micros() // 1000000)

    def __float__(self):
        """Convert to floating-point number of seconds since the epoch (gmt).
        """
        return self.micros() / 1000000.0

    @property
    def _t(self):
        return self._micros / 1000000.0

    def _parse_iso8601(self, s):
        # preserve the previously implied contract
        # who know where this could be used...
        return self._parse_iso8601_preserving_tznaive(s)[:7]

    def _parse_iso8601_preserving_tznaive(self, s):
        try:
            return self.__parse_iso8601(s)
        except IndexError:
            raise SyntaxError(
                'Not an ISO 8601 compliant date string: "%s"' % s)

    def __parse_iso8601(self, s):
        """Parse an ISO 8601 compliant date.

        See: http://en.wikipedia.org/wiki/ISO_8601
        """
        month = day = week_day = 1
        year = hour = minute = seconds = hour_off = min_off = 0
        tznaive = True

        iso8601 = iso8601Match(s.strip())
        fields = iso8601 and iso8601.groupdict() or {}
        if not iso8601 or fields.get('garbage'):
            raise IndexError

        if fields['year']:
            year = int(fields['year'])
        if fields['month']:
            month = int(fields['month'])
        if fields['day']:
            day = int(fields['day'])

        if fields['year_day']:
            d = DateTime('%s-01-01' % year) + int(fields['year_day']) - 1
            month = d.month()
            day = d.day()

        if fields['week']:
            week = int(fields['week'])
            if fields['week_day']:
                week_day = int(fields['week_day'])
            d = DateTime('%s-01-04' % year)
            d = d - (d.dow() + 6) % 7 + week * 7 + week_day - 8
            month = d.month()
            day = d.day()

        if fields['hour']:
            hour = int(fields['hour'])

        if fields['minute']:
            minute = int(fields['minute'])
        elif fields['fraction']:
            minute = 60.0 * float('0.%s' % fields['fraction'])
            seconds, minute = math.modf(minute)
            minute = int(minute)
            seconds = 60.0 * seconds
            # Avoid reprocess when handling seconds, bellow
            fields['fraction'] = None

        if fields['second']:
            seconds = int(fields['second'])
            if fields['fraction']:
                seconds = seconds + float('0.%s' % fields['fraction'])
        elif fields['fraction']:
            seconds = 60.0 * float('0.%s' % fields['fraction'])

        if fields['hour_off']:
            hour_off = int(fields['hour_off'])
            if fields['signal'] == '-':
                hour_off *= -1

        if fields['min_off']:
            min_off = int(fields['min_off'])

        if fields['signal'] or fields['Z']:
            tznaive = False
        else:
            tznaive = True

        # Differ from the specification here. To preserve backwards
        # compatibility assume a default timezone == UTC.
        tz = 'GMT%+03d%02d' % (hour_off, min_off)

        return year, month, day, hour, minute, seconds, tz, tznaive

    def JulianDay(self):
        """Return the Julian day.

        See: http://www.tondering.dk/claus/cal/node3.html#sec-calcjd
        """
        a = (14 - self._month) // 12
        y = self._year + 4800 - a
        m = self._month + (12 * a) - 3
        return (self._day + (153 * m + 2) // 5 + 365 * y +
            y // 4 - y // 100 + y // 400 - 32045)

    def week(self):
        """Return the week number according to ISO.

        See: http://www.tondering.dk/claus/cal/node6.html
        """
        J = self.JulianDay()
        d4 = (J + 31741 - (J % 7)) % 146097 % 36524 % 1461
        L = d4 // 1460
        d1 = ((d4 - L) % 365) + L
        return d1 // 7 + 1

    def encode(self, out):
        """Encode value for XML-RPC."""
        out.write('<value><dateTime.iso8601>')
        out.write(self.ISO8601())
        out.write('</dateTime.iso8601></value>\n')


# Provide the _dt_reconstructor function here, in case something
# accidentally creates a reference to this function

orig_reconstructor = copy_reg._reconstructor


def _dt_reconstructor(cls, base, state):
    if cls is DateTime:
        return cls(state)
    return orig_reconstructor(cls, base, state)
