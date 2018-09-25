from datetime import datetime, time
from django.utils import timezone


class DateOfYear:
    def __init__(self, year):
        self.year = year
        self.timezone = timezone.get_current_timezone()
        self.start_datetime = datetime(self.year, 1, 1).astimezone(self.timezone)
        self.end_datetime = datetime(self.year, 12, 31).astimezone(self.timezone)
        self.max_datetime = datetime.combine(self.end_date, time.max).astimezone(self.timezone)
        self.new_year_datetime = datetime(self.year + 1, 1, 1).astimezone(self.timezone)

    @property
    def start_date(self):
        return self.start_datetime.date()

    @property
    def end_date(self):
        return self.end_datetime.date()

    @property
    def new_year_date(self):
        return self.new_year_datetime.date()

    @property
    def start_date_yyyymmdd(self):
        return DateOfYear.to_yyyymmdd(self.start_datetime)

    @property
    def end_date_yyyymmdd(self):
        return DateOfYear.to_yyyymmdd(self.end_datetime)

    @property
    def new_year_date_yyyymmdd(self):
        return DateOfYear.to_yyyymmdd(self.new_year_datetime)

    @property
    def start_date_unixtime(self):
        return DateOfYear.to_unixtime(self.start_datetime)

    @property
    def end_date_unixtime(self):
        return DateOfYear.to_unixtime(self.end_datetime)

    @property
    def new_year_date_unixtime(self):
        return DateOfYear.to_unixtime(self.new_year_datetime)

    @property
    def min_unixtime(self):
        return self.start_date_unixtime

    @property
    def max_unixtime(self):
        return DateOfYear.to_unixtime(self.max_datetime)

    @staticmethod
    def to_yyyymmdd(dt):
        return dt.strftime('%Y%m%d')

    @staticmethod
    def to_unixtime(dt):
        return int(dt.timestamp())


def main():
    date_of_year = DateOfYear(2018)
    assert date_of_year.start_date_yyyymmdd == '20180101'
    assert date_of_year.end_date_yyyymmdd == '20181231'
    assert date_of_year.new_year_date_yyyymmdd == '20190101'
    assert date_of_year.start_date_unixtime == 1514732400
    assert date_of_year.end_date_unixtime == 1546182000
    assert date_of_year.new_year_date_unixtime == 1546268400
    assert date_of_year.min_unixtime == 1514732400
    assert date_of_year.max_unixtime == 1546268399

    print(date_of_year.start_date)


if __name__ == "__main__":
    main()