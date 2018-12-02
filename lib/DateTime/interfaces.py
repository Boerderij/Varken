##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
from zope.interface import Interface


class DateTimeError(Exception):
    pass


class SyntaxError(DateTimeError):
    pass


class DateError(DateTimeError):
    pass


class TimeError(DateTimeError):
    pass


class IDateTime(Interface):
    # Conversion and comparison methods

    #TODO determine whether this method really is part of the public API
    def localZone(ltm=None):
        '''Returns the time zone on the given date.  The time zone
        can change according to daylight savings.'''

    def timeTime():
        """Return the date/time as a floating-point number in UTC, in
        the format used by the python time module.  Note that it is
        possible to create date/time values with DateTime that have no
        meaningful value to the time module."""

    def toZone(z):
        """Return a DateTime with the value as the current object,
        represented in the indicated timezone."""

    def isFuture():
        """Return true if this object represents a date/time later
        than the time of the call"""

    def isPast():
        """Return true if this object represents a date/time earlier
        than the time of the call"""

    def isCurrentYear():
        """Return true if this object represents a date/time that
        falls within the current year, in the context of this
        object's timezone representation"""

    def isCurrentMonth():
        """Return true if this object represents a date/time that
        falls within the current month, in the context of this
        object's timezone representation"""

    def isCurrentDay():
        """Return true if this object represents a date/time that
        falls within the current day, in the context of this object's
        timezone representation"""

    def isCurrentHour():
        """Return true if this object represents a date/time that
        falls within the current hour, in the context of this object's
        timezone representation"""

    def isCurrentMinute():
        """Return true if this object represents a date/time that
        falls within the current minute, in the context of this
        object's timezone representation"""

    def isLeapYear():
        """Return true if the current year (in the context of the
        object's timezone) is a leap year"""

    def earliestTime():
        """Return a new DateTime object that represents the earliest
        possible time (in whole seconds) that still falls within the
        current object's day, in the object's timezone context"""

    def latestTime():
        """Return a new DateTime object that represents the latest
        possible time (in whole seconds) that still falls within the
        current object's day, in the object's timezone context"""

    def greaterThan(t):
        """Compare this DateTime object to another DateTime object OR
        a floating point number such as that which is returned by the
        python time module. Returns true if the object represents a
        date/time greater than the specified DateTime or time module
        style time.  Revised to give more correct results through
        comparison of long integer milliseconds."""

    __gt__ = greaterThan

    def greaterThanEqualTo(t):
        """Compare this DateTime object to another DateTime object OR
        a floating point number such as that which is returned by the
        python time module. Returns true if the object represents a
        date/time greater than or equal to the specified DateTime or
        time module style time.  Revised to give more correct results
        through comparison of long integer milliseconds."""

    __ge__ = greaterThanEqualTo

    def equalTo(t):
        """Compare this DateTime object to another DateTime object OR
        a floating point number such as that which is returned by the
        python time module. Returns true if the object represents a
        date/time equal to the specified DateTime or time module style
        time.  Revised to give more correct results through comparison
        of long integer milliseconds."""

    __eq__ = equalTo

    def notEqualTo(t):
        """Compare this DateTime object to another DateTime object OR
        a floating point number such as that which is returned by the
        python time module. Returns true if the object represents a
        date/time not equal to the specified DateTime or time module
        style time.  Revised to give more correct results through
        comparison of long integer milliseconds."""

    __ne__ = notEqualTo

    def lessThan(t):
        """Compare this DateTime object to another DateTime object OR
        a floating point number such as that which is returned by the
        python time module. Returns true if the object represents a
        date/time less than the specified DateTime or time module
        style time.  Revised to give more correct results through
        comparison of long integer milliseconds."""

    __lt__ = lessThan

    def lessThanEqualTo(t):
        """Compare this DateTime object to another DateTime object OR
        a floating point number such as that which is returned by the
        python time module. Returns true if the object represents a
        date/time less than or equal to the specified DateTime or time
        module style time.  Revised to give more correct results
        through comparison of long integer milliseconds."""

    __le__ = lessThanEqualTo

    # Component access

    def parts():
        """Return a tuple containing the calendar year, month, day,
        hour, minute second and timezone of the object"""

    def timezone():
        """Return the timezone in which the object is represented."""

    def tzoffset():
        """Return the timezone offset for the objects timezone."""

    def year():
        """Return the calendar year of the object"""

    def month():
        """Return the month of the object as an integer"""

    def Month():
        """Return the full month name"""

    def aMonth():
        """Return the abreviated month name."""

    def Mon():
        """Compatibility: see aMonth"""

    def pMonth():
        """Return the abreviated (with period) month name."""

    def Mon_():
        """Compatibility: see pMonth"""

    def day():
        """Return the integer day"""

    def Day():
        """Return the full name of the day of the week"""

    def DayOfWeek():
        """Compatibility: see Day"""

    def dayOfYear():
        """Return the day of the year, in context of the timezone
        representation of the object"""

    def aDay():
        """Return the abreviated name of the day of the week"""

    def pDay():
        """Return the abreviated (with period) name of the day of the
        week"""

    def Day_():
        """Compatibility: see pDay"""

    def dow():
        """Return the integer day of the week, where sunday is 0"""

    def dow_1():
        """Return the integer day of the week, where sunday is 1"""

    def h_12():
        """Return the 12-hour clock representation of the hour"""

    def h_24():
        """Return the 24-hour clock representation of the hour"""

    def ampm():
        """Return the appropriate time modifier (am or pm)"""

    def hour():
        """Return the 24-hour clock representation of the hour"""

    def minute():
        """Return the minute"""

    def second():
        """Return the second"""

    def millis():
        """Return the millisecond since the epoch in GMT."""

    def strftime(format):
        """Format the date/time using the *current timezone representation*."""

    # General formats from previous DateTime

    def Date():
        """Return the date string for the object."""

    def Time():
        """Return the time string for an object to the nearest second."""

    def TimeMinutes():
        """Return the time string for an object not showing seconds."""

    def AMPM():
        """Return the time string for an object to the nearest second."""

    def AMPMMinutes():
        """Return the time string for an object not showing seconds."""

    def PreciseTime():
        """Return the time string for the object."""

    def PreciseAMPM():
        """Return the time string for the object."""

    def yy():
        """Return calendar year as a 2 digit string"""

    def mm():
        """Return month as a 2 digit string"""

    def dd():
        """Return day as a 2 digit string"""

    def rfc822():
        """Return the date in RFC 822 format"""

    # New formats

    def fCommon():
        """Return a string representing the object's value in the
        format: March 1, 1997 1:45 pm"""

    def fCommonZ():
        """Return a string representing the object's value in the
        format: March 1, 1997 1:45 pm US/Eastern"""

    def aCommon():
        """Return a string representing the object's value in the
        format: Mar 1, 1997 1:45 pm"""

    def aCommonZ():
        """Return a string representing the object's value in the
        format: Mar 1, 1997 1:45 pm US/Eastern"""

    def pCommon():
        """Return a string representing the object's value in the
        format: Mar. 1, 1997 1:45 pm"""

    def pCommonZ():
        """Return a string representing the object's value
           in the format: Mar. 1, 1997 1:45 pm US/Eastern"""

    def ISO():
        """Return the object in ISO standard format. Note: this is
        *not* ISO 8601-format! See the ISO8601 and HTML4 methods below
        for ISO 8601-compliant output

        Dates are output as: YYYY-MM-DD HH:MM:SS
        """

    def ISO8601():
        """Return the object in ISO 8601-compatible format containing
        the date, time with seconds-precision and the time zone
        identifier - see http://www.w3.org/TR/NOTE-datetime

        Dates are output as: YYYY-MM-DDTHH:MM:SSTZD
            T is a literal character.
            TZD is Time Zone Designator, format +HH:MM or -HH:MM

        The HTML4 method below offers the same formatting, but
        converts to UTC before returning the value and sets the TZD"Z"
        """

    def HTML4():
        """Return the object in the format used in the HTML4.0
        specification, one of the standard forms in ISO8601.  See
        http://www.w3.org/TR/NOTE-datetime

        Dates are output as: YYYY-MM-DDTHH:MM:SSZ
           T, Z are literal characters.
           The time is in UTC.
        """

    def JulianDay():
        """Return the Julian day according to
        http://www.tondering.dk/claus/cal/node3.html#sec-calcjd
        """

    def week():
        """Return the week number according to ISO
        see http://www.tondering.dk/claus/cal/node6.html#SECTION00670000000000000000
        """

    # Python operator and conversion API

    def __add__(other):
        """A DateTime may be added to a number and a number may be
        added to a DateTime; two DateTimes cannot be added."""

    __radd__ = __add__

    def __sub__(other):
        """Either a DateTime or a number may be subtracted from a
        DateTime, however, a DateTime may not be subtracted from a
        number."""

    def __repr__():
        """Convert a DateTime to a string that looks like a Python
        expression."""

    def __str__():
        """Convert a DateTime to a string."""

    def __hash__():
        """Compute a hash value for a DateTime"""

    def __int__():
        """Convert to an integer number of seconds since the epoch (gmt)"""

    def __long__():
        """Convert to a long-int number of seconds since the epoch (gmt)"""

    def __float__():
        """Convert to floating-point number of seconds since the epoch (gmt)"""
