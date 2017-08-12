# Will be holiday class, with each country as separate subclass
# Is called by:
#   - datachecker

import datetime as dt


class Holiday(object):

    def __init__(self, country):
        self.country = country

    def holidays(self, year):
        if type(year) is int:
            year = str(year)

        if self.country == 'US':
            return self.days_off_US(year)

    def days_off_US(self, year):
        if type(year) is int:
            year = str(year)

        days_off_list = []
        # New Year's day
        new_years_day = dt.datetime.strptime(''.join([year, '-01-01']), '%Y-%m-%d').date()
        if new_years_day.weekday() == 6:
            new_years_day = dt.datetime.strptime(''.join([year, '-01-02']), '%Y-%m-%d').date()
        days_off_list.append(new_years_day)

        # Martin Luther King day (third Monday of January)
        first_day = dt.datetime.strptime(''.join([year, '-01-01']), '%Y-%m-%d').date()
        mlk_day = 15 if first_day.weekday() == 0 else 22 - first_day.weekday()
        mlk_day = dt.datetime.strptime(''.join([year, '-01-', str(mlk_day)]), '%Y-%m-%d').date()
        days_off_list.append(mlk_day)

        # President's day (third Monday of February)
        first_day = dt.datetime.strptime(''.join([year, '-02-01']), '%Y-%m-%d').date()
        pres_day = 15 if first_day.weekday() == 0 else 22 - first_day.weekday()
        pres_day = dt.datetime.strptime(''.join([year, '-02-', str(pres_day)]), '%Y-%m-%d').date()
        days_off_list.append(pres_day)

        # Good Friday (Friday somewhere in April/May)
        a = int(year) % 19
        b = int(year) >> 2
        c = b // 25 + 1
        d = (c * 3) >> 2
        e = ((a * 19) - ((c * 8 + 5) // 25) + d + 15) % 30
        e += (29578 - a - e * 32) >> 10
        e -= ((int(year) % 7) + b - d + e + 2) % 7
        d = e >> 5
        day = str(e - d * 31)
        month = str(d + 3)
        easter_sunday = dt.datetime.strptime(''.join([year, '-', month, '-', day]), '%Y-%m-%d').date()
        good_friday = easter_sunday + dt.timedelta(days=-2)
        days_off_list.append(good_friday)

        # Memorial day (last Monday of May)
        last_day = dt.datetime.strptime(''.join([year, '-05-31']), '%Y-%m-%d').date()
        mem_day = str(31 - last_day.weekday())
        mem_day = dt.datetime.strptime(''.join([year, '-05-', mem_day]), '%Y-%m-%d').date()
        days_off_list.append(mem_day)

        # Independence day (July 4th, or Monday after, Friday before)
        jul4 = dt.datetime.strptime(''.join([year, '-07-04']), '%Y-%m-%d').date()
        if jul4.weekday() == 5:
            jul4 = dt.datetime.strptime(''.join([year, '-07-03']), '%Y-%m-%d').date()
        elif jul4.weekday() == 6:
            jul4 = dt.datetime.strptime(''.join([year, '-07-05']), '%Y-%m-%d').date()
        days_off_list.append(jul4)

        # Labor day (first Monday in September)
        first_day = dt.datetime.strptime(''.join([year, '-09-01']), '%Y-%m-%d').date()
        lab_day = 1 if first_day.weekday() == 0 else 8 - first_day.weekday()
        lab_day = dt.datetime.strptime(''.join([year, '-09-', str(lab_day)]), '%Y-%m-%d').date()
        days_off_list.append(lab_day)

        # Thanksgiving day (fourth Thursday of November)
        first_day = dt.datetime.strptime(''.join([year, '-11-01']), '%Y-%m-%d').date()
        thanks = 25 - first_day.weekday() if first_day.weekday() < 4 else 32 - first_day.weekday()
        thanks = dt.datetime.strptime(''.join([year, '-11-', str(thanks)]), '%Y-%m-%d').date()
        days_off_list.append(thanks)

        # Christmas day (December 25th, or Monday after, Friday before)
        christ = dt.datetime.strptime(''.join([year, '-12-25']), '%Y-%m-%d').date()
        if christ.weekday() == 5:
            christ = dt.datetime.strptime(''.join([year, '-12-24']), '%Y-%m-%d').date()
        elif christ.weekday() == 6:
            christ = dt.datetime.strptime(''.join([year, '-12-26']), '%Y-%m-%d').date()
        days_off_list.append(christ)

        if year == '2001':
            # 9-11
            days_off_list.append(dt.datetime.strptime('2001-09-11', '%Y-%m-%d').date())
        if year == '2004':
            # Death president Ronald Reagan
            days_off_list.append(dt.datetime.strptime('2004-06-11', '%Y-%m-%d').date())
        if year == '2012':
            # Hurricane Sandy
            days_off_list.append(dt.datetime.strptime('2012-10-29', '%Y-%m-%d').date())

        return days_off_list
