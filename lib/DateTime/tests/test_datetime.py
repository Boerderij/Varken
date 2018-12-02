##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from datetime import date, datetime, tzinfo, timedelta
import math
import platform
import os
import sys
import time
import unittest

import pytz

from DateTime.DateTime import _findLocalTimeZoneName
from DateTime import DateTime

if sys.version_info > (3, ):
    import pickle
    unicode = str
    PY3K = True
else:
    import cPickle as pickle
    PY3K = False

try:
    __file__
except NameError:
    f = sys.argv[0]
else:
    f = __file__

IS_PYPY = getattr(platform, 'python_implementation', lambda: None)() == 'PyPy'

DATADIR = os.path.dirname(os.path.abspath(f))
del f

ZERO = timedelta(0)


class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO


class DateTimeTests(unittest.TestCase):

    def _compare(self, dt1, dt2):
        '''Compares the internal representation of dt1 with
        the representation in dt2.  Allows sub-millisecond variations.
        Primarily for testing.'''
        self.assertEqual(round(dt1._t, 3), round(dt2._t, 3))
        self.assertEqual(round(dt1._d, 9), round(dt2._d, 9))
        self.assertEqual(round(dt1.time, 9), round(dt2.time, 9))
        self.assertEqual(dt1.millis(), dt2.millis())
        self.assertEqual(dt1._micros, dt2._micros)

    def testBug1203(self):
        # 01:59:60 occurred in old DateTime
        dt = DateTime(7200, 'GMT')
        self.assertTrue(str(dt).find('60') < 0, dt)

    def testDSTInEffect(self):
        # Checks GMT offset for a DST date in the US/Eastern time zone
        dt = DateTime(2000, 5, 9, 15, 0, 0, 'US/Eastern')
        self.assertEqual(dt.toZone('GMT').hour(), 19,
                         (dt, dt.toZone('GMT')))

    def testDSTNotInEffect(self):
        # Checks GMT offset for a non-DST date in the US/Eastern time zone
        dt = DateTime(2000, 11, 9, 15, 0, 0, 'US/Eastern')
        self.assertEqual(dt.toZone('GMT').hour(), 20,
                         (dt, dt.toZone('GMT')))

    def testAddPrecision(self):
        # Precision of serial additions
        dt = DateTime()
        self.assertEqual(str(dt + 0.10 + 3.14 + 6.76 - 10), str(dt),
                         dt)

    def testConstructor3(self):
        # Constructor from date/time string
        dt = DateTime()
        dt1s = '%d/%d/%d %d:%d:%f %s' % (
            dt.year(),
            dt.month(),
            dt.day(),
            dt.hour(),
            dt.minute(),
            dt.second(),
            dt.timezone())
        dt1 = DateTime(dt1s)
        # Compare representations as it's the
        # only way to compare the dates to the same accuracy
        self.assertEqual(repr(dt), repr(dt1))

    def testConstructor4(self):
        # Constructor from time float
        dt = DateTime()
        dt1 = DateTime(float(dt))
        self._compare(dt, dt1)

    def testConstructor5(self):
        # Constructor from time float and timezone
        dt = DateTime()
        dt1 = DateTime(float(dt), dt.timezone())
        self.assertEqual(str(dt), str(dt1), (dt, dt1))
        dt1 = DateTime(float(dt), unicode(dt.timezone()))
        self.assertEqual(str(dt), str(dt1), (dt, dt1))

    def testConstructor6(self):
        # Constructor from year and julian date
        # This test must normalize the time zone, or it *will* break when
        # DST changes!
        dt1 = DateTime(2000, 5.500000578705)
        dt = DateTime('2000/1/5 12:00:00.050 pm %s' % dt1.localZone())
        self._compare(dt, dt1)

    def testConstructor7(self):
        # Constructor from parts
        dt = DateTime()
        dt1 = DateTime(
            dt.year(),
            dt.month(),
            dt.day(),
            dt.hour(),
            dt.minute(),
            dt.second(),
            dt.timezone())
        # Compare representations as it's the
        # only way to compare the dates to the same accuracy
        self.assertEqual(repr(dt), repr(dt1))

    def testDayOfWeek(self):
        # Compare to the datetime.date value to make it locale independent
        expected = date(2000, 6, 16).strftime('%A')
        # strftime() used to always be passed a day of week of 0
        dt = DateTime('2000/6/16')
        s = dt.strftime('%A')
        self.assertEqual(s, expected, (dt, s))

    def testOldDate(self):
        # Fails when an 1800 date is displayed with negative signs
        dt = DateTime('1830/5/6 12:31:46.213 pm')
        dt1 = dt.toZone('GMT+6')
        self.assertTrue(str(dt1).find('-') < 0, (dt, dt1))

    def testSubtraction(self):
        # Reconstruction of a DateTime from its parts, with subtraction
        # this also tests the accuracy of addition and reconstruction
        dt = DateTime()
        dt1 = dt - 3.141592653
        dt2 = DateTime(
            dt.year(),
            dt.month(),
            dt.day(),
            dt.hour(),
            dt.minute(),
            dt.second())
        dt3 = dt2 - 3.141592653
        self.assertEqual(dt1, dt3, (dt, dt1, dt2, dt3))

    def testTZ1add(self):
        # Time zone manipulation: add to a date
        dt = DateTime('1997/3/8 1:45am GMT-4')
        dt1 = DateTime('1997/3/9 1:45pm GMT+8')
        self.assertTrue((dt + 1.0).equalTo(dt1))

    def testTZ1sub(self):
        # Time zone manipulation: subtract from a date
        dt = DateTime('1997/3/8 1:45am GMT-4')
        dt1 = DateTime('1997/3/9 1:45pm GMT+8')
        self.assertTrue((dt1 - 1.0).equalTo(dt))

    def testTZ1diff(self):
        # Time zone manipulation: diff two dates
        dt = DateTime('1997/3/8 1:45am GMT-4')
        dt1 = DateTime('1997/3/9 1:45pm GMT+8')
        self.assertEqual(dt1 - dt, 1.0, (dt, dt1))

    def test_compare_methods(self):
        # Compare two dates using several methods
        dt = DateTime('1997/1/1')
        dt1 = DateTime('1997/2/2')
        self.assertTrue(dt1.greaterThan(dt))
        self.assertTrue(dt1.greaterThanEqualTo(dt))
        self.assertTrue(dt.lessThan(dt1))
        self.assertTrue(dt.lessThanEqualTo(dt1))
        self.assertTrue(dt.notEqualTo(dt1))
        self.assertFalse(dt.equalTo(dt1))

    def test_compare_methods_none(self):
        # Compare a date to None
        dt = DateTime('1997/1/1')
        self.assertTrue(dt.greaterThan(None))
        self.assertTrue(dt.greaterThanEqualTo(None))
        self.assertFalse(dt.lessThan(None))
        self.assertFalse(dt.lessThanEqualTo(None))
        self.assertTrue(dt.notEqualTo(None))
        self.assertFalse(dt.equalTo(None))

    def test_pickle(self):
        dt = DateTime()
        data = pickle.dumps(dt, 1)
        new = pickle.loads(data)
        for key in DateTime.__slots__:
            self.assertEqual(getattr(dt, key), getattr(new, key))

    def test_pickle_with_tz(self):
        dt = DateTime('2002/5/2 8:00am GMT+8')
        data = pickle.dumps(dt, 1)
        new = pickle.loads(data)
        for key in DateTime.__slots__:
            self.assertEqual(getattr(dt, key), getattr(new, key))

    def test_pickle_with_numerical_tz(self):
        for dt_str in ('2007/01/02 12:34:56.789 +0300',
                       '2007/01/02 12:34:56.789 +0430',
                       '2007/01/02 12:34:56.789 -1234'):
            dt = DateTime(dt_str)
            data = pickle.dumps(dt, 1)
            new = pickle.loads(data)
            for key in DateTime.__slots__:
                self.assertEqual(getattr(dt, key), getattr(new, key))

    def test_pickle_with_micros(self):
        dt = DateTime('2002/5/2 8:00:14.123 GMT+8')
        data = pickle.dumps(dt, 1)
        new = pickle.loads(data)
        for key in DateTime.__slots__:
            self.assertEqual(getattr(dt, key), getattr(new, key))

    def test_pickle_old(self):
        dt = DateTime('2002/5/2 8:00am GMT+0')
        data = ('(cDateTime.DateTime\nDateTime\nq\x01Noq\x02}q\x03(U\x05'
            '_amonq\x04U\x03Mayq\x05U\x05_adayq\x06U\x03Thuq\x07U\x05_pmonq'
            '\x08h\x05U\x05_hourq\tK\x08U\x05_fmonq\nh\x05U\x05_pdayq\x0bU'
            '\x04Thu.q\x0cU\x05_fdayq\rU\x08Thursdayq\x0eU\x03_pmq\x0fU\x02amq'
            '\x10U\x02_tq\x11GA\xcehy\x00\x00\x00\x00U\x07_minuteq\x12K\x00U'
            '\x07_microsq\x13L1020326400000000L\nU\x02_dq\x14G@\xe2\x12j\xaa'
            '\xaa\xaa\xabU\x07_secondq\x15G\x00\x00\x00\x00\x00\x00\x00\x00U'
            '\x03_tzq\x16U\x05GMT+0q\x17U\x06_monthq\x18K\x05U'
            '\x0f_timezone_naiveq\x19I00\nU\x04_dayq\x1aK\x02U\x05_yearq'
            '\x1bM\xd2\x07U\x08_nearsecq\x1cG\x00\x00\x00\x00\x00\x00\x00'
            '\x00U\x07_pmhourq\x1dK\x08U\n_dayoffsetq\x1eK\x04U\x04timeq'
            '\x1fG?\xd5UUUV\x00\x00ub.')
        if PY3K:
            data = data.encode('latin-1')
        new = pickle.loads(data)
        for key in DateTime.__slots__:
            self.assertEqual(getattr(dt, key), getattr(new, key))

    def test_pickle_old_without_micros(self):
        dt = DateTime('2002/5/2 8:00am GMT+0')
        data = ('(cDateTime.DateTime\nDateTime\nq\x01Noq\x02}q\x03(U\x05'
            '_amonq\x04U\x03Mayq\x05U\x05_adayq\x06U\x03Thuq\x07U\x05_pmonq'
            '\x08h\x05U\x05_hourq\tK\x08U\x05_fmonq\nh\x05U\x05_pdayq\x0bU'
            '\x04Thu.q\x0cU\x05_fdayq\rU\x08Thursdayq\x0eU\x03_pmq\x0fU'
            '\x02amq\x10U\x02_tq\x11GA\xcehy\x00\x00\x00\x00U\x07_minuteq'
            '\x12K\x00U\x02_dq\x13G@\xe2\x12j\xaa\xaa\xaa\xabU\x07_secondq'
            '\x14G\x00\x00\x00\x00\x00\x00\x00\x00U\x03_tzq\x15U\x05GMT+0q'
            '\x16U\x06_monthq\x17K\x05U\x0f_timezone_naiveq\x18I00\nU'
            '\x04_dayq\x19K\x02U\x05_yearq\x1aM\xd2\x07U\x08_nearsecq'
            '\x1bG\x00\x00\x00\x00\x00\x00\x00\x00U\x07_pmhourq\x1cK\x08U'
            '\n_dayoffsetq\x1dK\x04U\x04timeq\x1eG?\xd5UUUV\x00\x00ub.')
        if PY3K:
            data = data.encode('latin-1')
        new = pickle.loads(data)
        for key in DateTime.__slots__:
            self.assertEqual(getattr(dt, key), getattr(new, key))

    def testTZ2(self):
        # Time zone manipulation test 2
        dt = DateTime()
        dt1 = dt.toZone('GMT')
        s = dt.second()
        s1 = dt1.second()
        self.assertEqual(s, s1, (dt, dt1, s, s1))

    def testTZDiffDaylight(self):
        # Diff dates across daylight savings dates
        dt = DateTime('2000/6/8 1:45am US/Eastern')
        dt1 = DateTime('2000/12/8 12:45am US/Eastern')
        self.assertEqual(dt1 - dt, 183, (dt, dt1, dt1 - dt))

    def testY10KDate(self):
        # Comparison of a Y10K date and a Y2K date
        dt = DateTime('10213/09/21')
        dt1 = DateTime(2000, 1, 1)

        dsec = (dt.millis() - dt1.millis()) / 1000.0
        ddays = math.floor((dsec / 86400.0) + 0.5)

        self.assertEqual(ddays, 3000000, ddays)

    def test_tzoffset(self):
        # Test time-zone given as an offset

        # GMT
        dt = DateTime('Tue, 10 Sep 2001 09:41:03 GMT')
        self.assertEqual(dt.tzoffset(), 0)

        # Timezone by name, a timezone that hasn't got daylightsaving.
        dt = DateTime('Tue, 2 Mar 2001 09:41:03 GMT+3')
        self.assertEqual(dt.tzoffset(), 10800)

        # Timezone by name, has daylightsaving but is not in effect.
        dt = DateTime('Tue, 21 Jan 2001 09:41:03 PST')
        self.assertEqual(dt.tzoffset(), -28800)

        # Timezone by name, with daylightsaving in effect
        dt = DateTime('Tue, 24 Aug 2001 09:41:03 PST')
        self.assertEqual(dt.tzoffset(), -25200)

        # A negative numerical timezone
        dt = DateTime('Tue, 24 Jul 2001 09:41:03 -0400')
        self.assertEqual(dt.tzoffset(), -14400)

        # A positive numerical timzone
        dt = DateTime('Tue, 6 Dec 1966 01:41:03 +0200')
        self.assertEqual(dt.tzoffset(), 7200)

        # A negative numerical timezone with minutes.
        dt = DateTime('Tue, 24 Jul 2001 09:41:03 -0637')
        self.assertEqual(dt.tzoffset(), -23820)

        # A positive numerical timezone with minutes.
        dt = DateTime('Tue, 24 Jul 2001 09:41:03 +0425')
        self.assertEqual(dt.tzoffset(), 15900)

    def testISO8601(self):
        # ISO8601 reference dates
        ref0 = DateTime('2002/5/2 8:00am GMT')
        ref1 = DateTime('2002/5/2 8:00am US/Eastern')
        ref2 = DateTime('2006/11/6 10:30 GMT')
        ref3 = DateTime('2004/06/14 14:30:15 GMT-3')
        ref4 = DateTime('2006/01/01 GMT')

        # Basic tests
        # Though this is timezone naive and according to specification should
        # be interpreted in the local timezone, to preserve backwards
        # compatibility with previously expected behaviour.
        isoDt = DateTime('2002-05-02T08:00:00')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002-05-02T08:00:00Z')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002-05-02T08:00:00+00:00')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002-05-02T08:00:00-04:00')
        self.assertTrue(ref1.equalTo(isoDt))
        isoDt = DateTime('2002-05-02 08:00:00-04:00')
        self.assertTrue(ref1.equalTo(isoDt))

        # Bug 1386: the colon in the timezone offset is optional
        isoDt = DateTime('2002-05-02T08:00:00-0400')
        self.assertTrue(ref1.equalTo(isoDt))

        # Bug 2191: date reduced formats
        isoDt = DateTime('2006-01-01')
        self.assertTrue(ref4.equalTo(isoDt))
        isoDt = DateTime('200601-01')
        self.assertTrue(ref4.equalTo(isoDt))
        isoDt = DateTime('20060101')
        self.assertTrue(ref4.equalTo(isoDt))
        isoDt = DateTime('2006-01')
        self.assertTrue(ref4.equalTo(isoDt))
        isoDt = DateTime('200601')
        self.assertTrue(ref4.equalTo(isoDt))
        isoDt = DateTime('2006')
        self.assertTrue(ref4.equalTo(isoDt))

        # Bug 2191: date/time separators are also optional
        isoDt = DateTime('20020502T08:00:00')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002-05-02T080000')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('20020502T080000')
        self.assertTrue(ref0.equalTo(isoDt))

        # Bug 2191: timezones with only one digit for hour
        isoDt = DateTime('20020502T080000+0')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('20020502 080000-4')
        self.assertTrue(ref1.equalTo(isoDt))
        isoDt = DateTime('20020502T080000-400')
        self.assertTrue(ref1.equalTo(isoDt))
        isoDt = DateTime('20020502T080000-4:00')
        self.assertTrue(ref1.equalTo(isoDt))

        # Bug 2191: optional seconds/minutes
        isoDt = DateTime('2002-05-02T0800')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002-05-02T08')
        self.assertTrue(ref0.equalTo(isoDt))

        # Bug 2191: week format
        isoDt = DateTime('2002-W18-4T0800')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002-W184T0800')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002W18-4T0800')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002W184T08')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2004-W25-1T14:30:15-03:00')
        self.assertTrue(ref3.equalTo(isoDt))
        isoDt = DateTime('2004-W25T14:30:15-03:00')
        self.assertTrue(ref3.equalTo(isoDt))

        # Bug 2191: day of year format
        isoDt = DateTime('2002-122T0800')
        self.assertTrue(ref0.equalTo(isoDt))
        isoDt = DateTime('2002122T0800')
        self.assertTrue(ref0.equalTo(isoDt))

        # Bug 2191: hours/minutes fractions
        isoDt = DateTime('2006-11-06T10.5')
        self.assertTrue(ref2.equalTo(isoDt))
        isoDt = DateTime('2006-11-06T10,5')
        self.assertTrue(ref2.equalTo(isoDt))
        isoDt = DateTime('20040614T1430.25-3')
        self.assertTrue(ref3.equalTo(isoDt))
        isoDt = DateTime('2004-06-14T1430,25-3')
        self.assertTrue(ref3.equalTo(isoDt))
        isoDt = DateTime('2004-06-14T14:30.25-3')
        self.assertTrue(ref3.equalTo(isoDt))
        isoDt = DateTime('20040614T14:30,25-3')
        self.assertTrue(ref3.equalTo(isoDt))

        # ISO8601 standard format
        iso8601_string = '2002-05-02T08:00:00-04:00'
        iso8601DT = DateTime(iso8601_string)
        self.assertEqual(iso8601_string, iso8601DT.ISO8601())

        # ISO format with no timezone
        isoDt = DateTime('2006-01-01 00:00:00')
        self.assertTrue(ref4.equalTo(isoDt))

    def testJulianWeek(self):
        # Check JulianDayWeek function
        fn = os.path.join(DATADIR, 'julian_testdata.txt')
        with open(fn, 'r') as fd:
            lines = fd.readlines()
        for line in lines:
            d = DateTime(line[:10])
            result_from_mx = tuple(map(int, line[12:-2].split(',')))
            self.assertEqual(result_from_mx[1], d.week())

    def testCopyConstructor(self):
        d = DateTime('2004/04/04')
        self.assertEqual(DateTime(d), d)
        self.assertEqual(str(DateTime(d)), str(d))
        d2 = DateTime('1999/04/12 01:00:00')
        self.assertEqual(DateTime(d2), d2)
        self.assertEqual(str(DateTime(d2)), str(d2))

    def testCopyConstructorPreservesTimezone(self):
        # test for https://bugs.launchpad.net/zope2/+bug/200007
        # This always worked in the local timezone, so we need at least
        # two tests with different zones to be sure at least one of them
        # is not local.
        d = DateTime('2004/04/04')
        self.assertEqual(DateTime(d).timezone(), d.timezone())
        d2 = DateTime('2008/04/25 12:00:00 EST')
        self.assertEqual(DateTime(d2).timezone(), d2.timezone())
        self.assertEqual(str(DateTime(d2)), str(d2))
        d3 = DateTime('2008/04/25 12:00:00 PST')
        self.assertEqual(DateTime(d3).timezone(), d3.timezone())
        self.assertEqual(str(DateTime(d3)), str(d3))

    def testRFC822(self):
        # rfc822 conversion
        dt = DateTime('2002-05-02T08:00:00+00:00')
        self.assertEqual(dt.rfc822(), 'Thu, 02 May 2002 08:00:00 +0000')

        dt = DateTime('2002-05-02T08:00:00+02:00')
        self.assertEqual(dt.rfc822(), 'Thu, 02 May 2002 08:00:00 +0200')

        dt = DateTime('2002-05-02T08:00:00-02:00')
        self.assertEqual(dt.rfc822(), 'Thu, 02 May 2002 08:00:00 -0200')

        # Checking that conversion from local time is working.
        dt = DateTime()
        dts = dt.rfc822().split(' ')
        times = dts[4].split(':')
        _isDST = time.localtime(time.time())[8]
        if _isDST:
            offset = time.altzone
        else:
            offset = time.timezone
        self.assertEqual(dts[0], dt.aDay() + ',')
        self.assertEqual(int(dts[1]), dt.day())
        self.assertEqual(dts[2], dt.aMonth())
        self.assertEqual(int(dts[3]), dt.year())
        self.assertEqual(int(times[0]), dt.h_24())
        self.assertEqual(int(times[1]), dt.minute())
        self.assertEqual(int(times[2]), int(dt.second()))
        self.assertEqual(dts[5], "%+03d%02d" % divmod((-offset / 60), 60))

    def testInternationalDateformat(self):
        for year in (1990, 2001, 2020):
            for month in (1, 12):
                for day in (1, 12, 28, 31):
                    try:
                        d_us = DateTime("%d/%d/%d" % (year, month, day))
                    except Exception:
                        continue

                    d_int = DateTime("%d.%d.%d" % (day, month, year),
                                     datefmt="international")
                    self.assertEqual(d_us, d_int)

                    d_int = DateTime("%d/%d/%d" % (day, month, year),
                                     datefmt="international")
                    self.assertEqual(d_us, d_int)

    def test_intl_format_hyphen(self):
        d_jan = DateTime('2011-01-11 GMT')
        d_nov = DateTime('2011-11-01 GMT')
        d_us = DateTime('11-01-2011 GMT')
        d_int = DateTime('11-01-2011 GMT', datefmt="international")
        self.assertNotEqual(d_us, d_int)
        self.assertEqual(d_us, d_nov)
        self.assertEqual(d_int, d_jan)

    def test_calcTimezoneName(self):
        from DateTime.interfaces import TimeError
        timezone_dependent_epoch = 2177452800
        try:
            DateTime()._calcTimezoneName(timezone_dependent_epoch, 0)
        except TimeError:
            self.fail('Zope Collector issue #484 (negative time bug): '
                      'TimeError raised')

    def testStrftimeTZhandling(self):
        # strftime timezone testing
        # This is a test for collector issue #1127
        format = '%Y-%m-%d %H:%M %Z'
        dt = DateTime('Wed, 19 Nov 2003 18:32:07 -0215')
        dt_string = dt.strftime(format)
        dt_local = dt.toZone(_findLocalTimeZoneName(0))
        dt_localstring = dt_local.strftime(format)
        self.assertEqual(dt_string, dt_localstring)

    def testStrftimeFarDates(self):
        # Checks strftime in dates <= 1900 or >= 2038
        dt = DateTime('1900/01/30')
        self.assertEqual(dt.strftime('%d/%m/%Y'), '30/01/1900')
        dt = DateTime('2040/01/30')
        self.assertEqual(dt.strftime('%d/%m/%Y'), '30/01/2040')

    def testZoneInFarDates(self):
        # Checks time zone in dates <= 1900 or >= 2038
        dt1 = DateTime('2040/01/30 14:33 GMT+1')
        dt2 = DateTime('2040/01/30 11:33 GMT-2')
        self.assertEqual(dt1.strftime('%d/%m/%Y %H:%M'),
                         dt2.strftime('%d/%m/%Y %H:%M'))

    def testStrftimeUnicode(self):
        if IS_PYPY:
            # Using Non-Ascii characters for strftime doesn't work in PyPy
            # https://bitbucket.org/pypy/pypy/issues/2161/pypy3-strftime-does-not-accept-unicode
            return
        dt = DateTime('2002-05-02T08:00:00+00:00')
        uchar = b'\xc3\xa0'.decode('utf-8')
        ok = dt.strftime('Le %d/%m/%Y a %Hh%M').replace('a', uchar)
        ustr = b'Le %d/%m/%Y \xc3\xa0 %Hh%M'.decode('utf-8')
        self.assertEqual(dt.strftime(ustr), ok)

    def testTimezoneNaiveHandling(self):
        # checks that we assign timezone naivity correctly
        dt = DateTime('2007-10-04T08:00:00+00:00')
        self.assertFalse(dt.timezoneNaive(),
            'error with naivity handling in __parse_iso8601')
        dt = DateTime('2007-10-04T08:00:00Z')
        self.assertFalse(dt.timezoneNaive(),
            'error with naivity handling in __parse_iso8601')
        dt = DateTime('2007-10-04T08:00:00')
        self.assertTrue(dt.timezoneNaive(),
            'error with naivity handling in __parse_iso8601')
        dt = DateTime('2007/10/04 15:12:33.487618 GMT+1')
        self.assertFalse(dt.timezoneNaive(),
            'error with naivity handling in _parse')
        dt = DateTime('2007/10/04 15:12:33.487618')
        self.assertTrue(dt.timezoneNaive(),
            'error with naivity handling in _parse')
        dt = DateTime()
        self.assertFalse(dt.timezoneNaive(),
            'error with naivity for current time')
        s = '2007-10-04T08:00:00'
        dt = DateTime(s)
        self.assertEqual(s, dt.ISO8601())
        s = '2007-10-04T08:00:00+00:00'
        dt = DateTime(s)
        self.assertEqual(s, dt.ISO8601())

    def testConversions(self):
        sdt0 = datetime.now()  # this is a timezone naive datetime
        dt0 = DateTime(sdt0)
        self.assertTrue(dt0.timezoneNaive(), (sdt0, dt0))
        sdt1 = datetime(2007, 10, 4, 18, 14, 42, 580, pytz.utc)
        dt1 = DateTime(sdt1)
        self.assertFalse(dt1.timezoneNaive(), (sdt1, dt1))

        # convert back
        sdt2 = dt0.asdatetime()
        self.assertEqual(sdt0, sdt2)
        sdt3 = dt1.utcdatetime()  # this returns a timezone naive datetime
        self.assertEqual(sdt1.hour, sdt3.hour)

        dt4 = DateTime('2007-10-04T10:00:00+05:00')
        sdt4 = datetime(2007, 10, 4, 5, 0)
        self.assertEqual(dt4.utcdatetime(), sdt4)
        self.assertEqual(dt4.asdatetime(), sdt4.replace(tzinfo=pytz.utc))

        dt5 = DateTime('2007-10-23 10:00:00 US/Eastern')
        tz = pytz.timezone('US/Eastern')
        sdt5 = datetime(2007, 10, 23, 10, 0, tzinfo=tz)
        dt6 = DateTime(sdt5)
        self.assertEqual(dt5.asdatetime(), sdt5)
        self.assertEqual(dt6.asdatetime(), sdt5)
        self.assertEqual(dt5, dt6)
        self.assertEqual(dt5.asdatetime().tzinfo, tz)
        self.assertEqual(dt6.asdatetime().tzinfo, tz)

    def testBasicTZ(self):
        # psycopg2 supplies it's own tzinfo instances, with no `zone` attribute
        tz = FixedOffset(60, 'GMT+1')
        dt1 = datetime(2008, 8, 5, 12, 0, tzinfo=tz)
        DT = DateTime(dt1)
        dt2 = DT.asdatetime()
        offset1 = dt1.tzinfo.utcoffset(dt1)
        offset2 = dt2.tzinfo.utcoffset(dt2)
        self.assertEqual(offset1, offset2)

    def testEDTTimezone(self):
        # should be able to parse EDT timezones:  see lp:599856.
        dt = DateTime("Mon, 28 Jun 2010 10:12:25 EDT")
        self.assertEqual(dt.Day(), 'Monday')
        self.assertEqual(dt.day(), 28)
        self.assertEqual(dt.Month(), 'June')
        self.assertEqual(dt.timezone(), 'GMT-4')

    def testParseISO8601(self):
        parsed = DateTime()._parse_iso8601('2010-10-10')
        self.assertEqual(parsed, (2010, 10, 10, 0, 0, 0, 'GMT+0000'))

    def test_interface(self):
        from DateTime.interfaces import IDateTime
        self.assertTrue(IDateTime.providedBy(DateTime()))

    def test_security(self):
        dt = DateTime()
        self.assertEqual(dt.__roles__, None)
        self.assertEqual(dt.__allow_access_to_unprotected_subobjects__, 1)


def test_suite():
    import doctest
    return unittest.TestSuite([
        unittest.makeSuite(DateTimeTests),
        doctest.DocFileSuite('DateTime.txt', package='DateTime'),
        doctest.DocFileSuite('pytz.txt', package='DateTime'),
    ])
