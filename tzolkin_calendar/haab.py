# SPDX-License-Identifier: MIT
# Portions (C) 2023 Jeremy Mahler
# Original codebase (C) 2021 Roland Csaszar
#
# Project:  mayan-calendar
# File:     haab.py
# Date:     7.Sep.2023
###############################################################################
"""Main Haab class."""

from __future__ import annotations

import datetime
from typing import List, Optional

from tzolkin_calendar.calculate import (
    calculateTzolkinName,
    calculateTzolkinNumber,
    getTzolkinDay,
    getTzolkinDiff,
    gregorian2tzolkin,
    lastTzolkin,
    makeLookUpTable,
    nextTzolkin,
    parseTzolkinName,
    tzolkin2gregorian,
)

from . import TzolkinDate, TzolkinException, TzolkinName, day_names, day_numbers


class Haab:
    """A representation of a Haab date.
    Use to do calculations and conversions from and to gregorian dates to Haab dates
    and search for days.
    """

    ############################################################################
    def __init__(
        self,
        number: int,
        name_str: Optional[str] = None,
        name_number: Optional[int] = None,
    ) -> None:
        """Generate a Haab date, from the haab day number `number` and the
        Haab day name `name_str` or `name_number`.
        The valid day names for `hname_str` are: "Pop", "Woʼ", "Sip", "Sotzʼ",
        "Tzek", "Xul", "Yaxkʼin", "Mol", "Chʼen", "Yax", "Sakʼ", "Keh", "Mak",
        "Kʼankʼin", "Muwanʼ", "Pax", "Kʼayab", "Kumkʼu", and "Wayeb'".

        You can also set the Haab day name using the argument `name_number`, which
        takes an integer between 1 and 19 (including 1 and 19).

        If you set both `name_number` and `name_str` to something else than `None`,
        `name_str` takes precedence.

        Raises:
            HaabException: if one of the parameters isn't valid.
                                That means, if `number` is not in [0,19], `name_number`
                                is not in [1, 19] or `name_str` is not a valid Haab
                                day name.

        Args:
            number (HaabNumber): [description]
            name_str (Optional[HaabName], optional): [description]. Defaults to None.
            name_number (Optional[HaabNameNumber], optional): [description]. Defaults to None.
        """
        name_num: int = 1
        num_num = number
        if name_str is not None:
            self.__checkNameString(name_str)

            name_num = self.getNameNumberFromName(name_str)

        elif name_number is not None:
            self.__checkNameNumber(name_number)
            name_num = name_number

        self.__checkDayNumber(number)

        self.__haab_date = HaabDate(number=num_num, name=name_num)

    ############################################################################
    @classmethod
    def fromDate(cls, date: datetime.date) -> Haab:
        """Create a `Haab` instance from the given gregorian date.

        Args:
            date (datetime.date): The date to convert to a Haab date.

        Returns:
            Haab: The gregorion date `date` converted to a Haab date.
        """
        haab = gregorian2haab(date)

        ret_val = cls(number=haab.number, name_number=haab.name)

        return ret_val

    ############################################################################
    @classmethod
    def fromDateString(cls, date_str: str, fmt: str) -> Haab:
        """Create a `Haab` instance from the given gregorian date string.
        See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        for a detailed description of date format strings.

        Args:
            date_str (str): The date to convert to a Haab date.
            fmt (str): The format string to parse the given date string. See
            `datetime.datetime.strptime` for a description of date format strings.

        Returns:
            Haab: The gregorion date `date_str` converted to a Haab date.
        """
        date = datetime.datetime.strptime(date_str, fmt).date()
        haab = gregorian2haab(date)

        ret_val = cls(number=haab.number, name_number=haab.name)

        return ret_val

    ############################################################################
    @classmethod
    def fromIsoFormat(cls, date_str: str) -> Haab:
        """Create a `Haab` instance from the given gregorian date string in ISO
        format.
        ISO format means a date in the form 'YYYY-MM-DD', like '2019-03-21'.
        See https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat

        Args:
            date_str (str): See also `datetime.date.fromisoformat`

        Returns:
            Haab: The gregorion date `date_str` converted to a Haab date.
        """
        date = datetime.date.fromisoformat(date_str)
        haab = gregorian2haab(date)

        ret_val = cls(number=haab.number, name_number=haab.name)

        return ret_val

    ############################################################################
    @classmethod
    def fromToday(cls) -> Haab:
        """Return the current date (today) as a Haab date.

        Returns:
            Haab: The current day (today) as a Haab date.
        """
        return cls.fromDate(datetime.date.today())

    ############################################################################
    def getHaabDate(self) -> HaabDate:
        """Return the Haab date as a `HaabDate` instance to use with the
        `haab_calendar.calculate` functions.

        Returns:
            HaabDate: The `HaabDate` instance of this Haab date.
        """
        return self.__haab_date

    ############################################################################
    def getDayNumber(self) -> int:
        """Return the day number of the Haab date of this class instance.

        Returns:
            int: The day number of this Haab date.
        """
        return self.__haab_date.number

    ############################################################################
    def getDayName(self) -> str:
        """Return the day name of the Haab date of this class instance.

        Returns:
            str: The day name of this Haab date.
        """
        return day_names[self.__haab_date.name]

    ############################################################################
    def getDayNameNumber(self) -> int:
        """Return the number of the Haab day name of this class instance.

        Returns:
            int: The number of the Haab day name of this Haab date.
        """
        return self.__haab_date.name

    ############################################################################
    def getHaabYearDay(self) -> int:
        """Return the day of the Haab year of this Haab date.
         0 Pop, the first day in the Haab year, yields 1, 5 Wayebʼ, the last day of
         the Haab year, yields 365 and so on.

        Returns:
             int: The day of this Haab date in the Haab year, an integer between
                 1 and 365 (including 1 and 365).
        """
        return getHaabDay(self.__haab_date)

    ############################################################################
    def getNextDate(
        self, start_date: datetime.date = datetime.date.today()
    ) -> datetime.date:
        """Return the next gregorian date with the Haab date of this Haab instance.
        Next means the first gregorian date with the same Haab date as this `Haab`
        instance after (forward in time) `start_date`.

        Args:
            start_date (datetime.date, optional): The date to start searching for a day
                        with the same Haab date. Defaults to `datetime.date.today()`.

        Returns:
            datetime.date: The gregorian date of the day with the same Haab date as
                            this `Haab` instance after `start_date`.
        """
        return nextHaab(haab=self.__haab_date, starting=start_date)

    ############################################################################
    def getNextDateList(
        self, start_date: datetime.date = datetime.date.today(), list_size: int = 50
    ) -> List[datetime.date]:
        """Return a list of dates with the same Haab date as this `Haab` instance
        after `start_date`.
        Searches forwards in time, starting with `start_date`.
        The number of elements in this returned list is set with `list_size`, that is
        the number of dates to search and return. If `list_size` < 1, an empty list is
        returned.

        Args:
            start_date (datetime.date, optional): The date to start searching for a day
                            with the same Haab date. Defaults to datetime.date.today().
            list_size (int, optional): The number of elements in the returned list of
                                        dates. Defaults to 50.

        Returns:
            List[datetime.date]: The list with `list_size` elements of days with the
                            same Haab date as this instance after `start_date`.
        """
        return haab2gregorian(
            haab=self.__haab_date,
            start=start_date,
            num_results=list_size,
            forward=True,
        )

    ############################################################################
    def getLastDate(
        self, start_date: datetime.date = datetime.date.today()
    ) -> datetime.date:
        """Return the last gregorian date with the Haab date of this Haab instance.
        Last means the first gregorian date with the same Haab date as this `Haab`
        instance before (backwards in time) `start_date`.

        Args:
            start_date (datetime.date, optional):  The date to start searching for a day
                          with the same Haab date. Defaults to datetime.date.today().

        Returns:
            datetime.date: The gregorian date of the day with the same Haab date as
                            this `Haab` instance before `start_date`.
        """
        return lastHaab(haab=self.__haab_date, starting=start_date)

    ############################################################################
    def getLastDateList(
        self, start_date: datetime.date = datetime.date.today(), list_size: int = 50
    ) -> List[datetime.date]:
        """Return a list of dates with the same Haab date as this `Haab` instance
        before`start_date`.
        Searches backwards in time, starting with `start_date`.
        The number of elements in this returned list is set with `list_size`, that is
        the number of dates to search and return. If `list_size` < 1, an empty list is
        returned.

        Args:
            start_date (datetime.date, optional): The date to start searching for a day
                            with the same Haab date. Defaults to datetime.date.today().
            list_size (int, optional): The number of elements in the returned list of
                                        dates. Defaults to 50.

        Returns:
            List[datetime.date]: The list with `list_size` elements of days with the
                            same Haab date as this instance before `start_date`.
        """
        return haab2gregorian(
            haab=self.__haab_date,
            start=start_date,
            num_results=list_size,
            forward=False,
        )

    ############################################################################
    def addDays(self, days: int) -> Haab:
        """Add the number of days to this Haab date and return this instance too.

        Args:
            days (int): The number of days to add (or subtract, if < 0) to this
                        `Haab` instance.

        Returns:
            Haab: This instance with the number of days added (or subtracted) to it.
        """
        added_name = calculateHaabName(
            start_name=self.__haab_date.name, to_add=days
        )
        added_number = calculateHaabNumber(
            start_number=self.__haab_date.number, to_add=days
        )
        self.__haab_date = HaabDate(number=added_number, name=added_name)
        return self

    ############################################################################
    def addTimedelta(self, delta: datetime.timedelta) -> Haab:
        """Add the number of days given in the `datetime.timedelta` object to this
        Haab date.
        Returns this `Haab` instance with the days added to or subtracted from.

        Args:
            delta (datetime.timedelta): The number of days to add (or subtract, if < 0).

        Returns:
            Haab: This instance with the number of days added or subtracted.
        """
        return self.addDays(days=delta.days)

    ############################################################################
    def getDayDiff(self, other: Haab) -> int:
        """Return the number of days between the two Haab dates.
        No negative differences are returned, but the number of days to reach the
        `other` date if starting from this Haab date.
        If this date is earlier than `other` the difference is
        `this` - `other`. If `other` is before `this`, 365 - `this` + `other`
        (same as 365 - (`other` - `this`)) is returned.

        Args:
            other (Haab): The Haab date to calculate the time difference to.

        Returns:
            int: The number of days between the Haab date of this `Haab` instance
                and the Haab date `other`.
        """
        return getHaabDiff(start=self.__haab_date, end=other.__haab_date)

    ############################################################################
    def getDayTimedelta(self, other: Haab) -> datetime.timedelta:
        """Return the number of days between the two Haab dates as a
        `datetime.timedelta` object.
        No negative differences are returned, but the number of days to reach the
        `other` date if starting from this Haab date.
        If this date is earlier than `other` the difference is
        `this` - `other`. If `other` is before `this`, 365 - `this` + `other`
        (same as 365 - (`other` - `this`)) is returned.

        Args:
            other (Haab): The Haab date to calculate the time difference to.

        Returns:
            datetime.timedelta: The number of days between the Haab date of this `Haab` instance
                and the Haab date `other` as a `datetime.timedelta` object.
        """
        days = getHaabDiff(start=self.__haab_date, end=other.__haab_date)
        return datetime.timedelta(days=days)

    ############################################################################
    @staticmethod
    def getNameNumberFromName(name_str: str) -> int:
        """Return the day name's number (between 1 and 19) of the Haab day name.
        Pop yields the number 1, Woʼ 2, ... , Wayebʼ yields 19.

        Args:
            name_str (HaabName): The day name to convert to a number.

        Raises:
            HaabException: Raised, if `name_str` is not a valid `HaabName`, that
            is, one of "Pop", "Woʼ", "Sip", "Sotzʼ",
        "Tzek", "Xul", "Yaxkʼin", "Mol", "Chʼen", "Yax", "Sakʼ", "Keh", "Mak",
        "Kʼankʼin", "Muwanʼ", "Pax", "Kʼayab", "Kumkʼu", and "Wayebʼ".

        Returns:
            int: The number of the Haab day name, between 1 and 19 (including 1 and
                19).
        """
        for num, name in day_names.items():
            if name.upper() == name_str.upper():
                return num

        raise HaabException(
            'string "{name}" is not a valid Haab day name, one of {list}'.format(
                name=name_str, list=day_names.values()
            )
        )

    ############################################################################
    @staticmethod
    def parseHaabName(name_str: str) -> int:
        """Parse the given string to get a valid Haab name.
        Ignores lower- and uppercase and all non-alphanumeric or non-ASCII letters.

        Returns 0 if no Haab day names matches the given string.

        Args:
            name_str (str): The string to parse for a Haab day name.

        Returns:
            int: The number of the Haab day name on success, 0 if no Haab day name
                    matches.
        """
        return parseHaabName(name_str=name_str)

    ############################################################################
    @staticmethod
    def getHaabCalendar() -> List[str]:
        """Return all days in a Haab year as a List of strings.
        The returned List looks like: ["0 Pop", "1 Pop", ... , "5 Wayebʼ"]

        Returns:
            List[str]: All days with day number and name in a list of strings.
        """
        ret_val: List[str] = []
        haab_list = makeLookUpTable()
        for haab_date in haab_list.values():
            ret_val.append(haab_date.__repr__())

        return ret_val

    ############################################################################
    @staticmethod
    def __checkDayNumber(number: int) -> None:
        """Check, if the given number is a valid Haab day number, that is, between 1
        and 13 (including 1 and 13).

        Args:
            number (HaabNumber): The integer to check.

        Raises:
            HaabException: If `number` is not in [0, 19] (including 0 and 19)
        """
        if number not in day_numbers.keys():
            raise HaabException(
                "number {num} is not a valid Haab day number, not between 0 and 19 (including 0 and 19)".format(
                    num=number
                )
            )

    ############################################################################
    @staticmethod
    def __checkNameNumber(name_number: int) -> None:
        """Check, if the given integer is a valid day name number, that is, between 1
        and 19, including 1 and 19.

        Args:
            name_number (HaabNameNumber): The number to check.

        Raises:
            HaabException: If `number` is not in [1, 19] (including 1 and 19).
        """
        if name_number not in day_names:
            raise HaabException(
                "{number} is not a valid Haab day name number, it must be between 1 and 19 (including 1 and 19)".format(
                    number=name_number
                )
            )

    ############################################################################
    @staticmethod
    def __checkNameString(name_str: HaabName) -> None:
        """Check, if the given string is a valid Haab day name.
         The valid day names for `name_str` are: "Pop", "Woʼ", "Sip", "Sotzʼ",
        "Tzek", "Xul", "Yaxkʼin", "Mol", "Chʼen", "Yax", "Sakʼ", "Keh", "Mak",
        "Kʼankʼin", "Muwanʼ", "Pax", "Kʼayab", "Kumkʼu", and "Wayebʼ".

        Args:
            name_str (HaabName): The string to check.

        Raises:
            HaabException: If `name_str` is not a valid Haab day name.
        """
        if name_str not in day_names.values():
            raise HaabException(
                'string "{name}" is not a valid Haab day name, one of: {list}'.format(
                    name=name_str, list=day_names.values()
                )
            )

    ############################################################################
    def __repr__(self) -> str:
        """Return the string representation of a Haab date.
        Return a string containing day number, day name and the day name's glyph in
        Unicode - that works as soon as the Maya glyphs are added to the standard.

        Returns:
            str: The string representation of a Haab date.
        """
        return self.__haab_date.__repr__()
