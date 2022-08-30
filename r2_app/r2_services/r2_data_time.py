# from django.utils.timezone import now
from datetime import datetime
import time as py_time
import pytz

import math


class R2DateTime:

    @staticmethod
    def humanize_date(date_to_convert):

        human_day = date_to_convert.day
        human_month = date_to_convert.month
        human_year = date_to_convert.year

        human_hour = date_to_convert.hour
        if human_hour > 12:
            a_m_p_m = ' pm'
            human_hour = human_hour - 12
        else:
            a_m_p_m = ' am'
        if human_hour is 0:
            human_hour = 12

        human_minute = date_to_convert.minute

        human_time = '%s:%s' % (R2DateTime.zeroing(human_hour), R2DateTime.zeroing(human_minute))

        if R2DateTime.is_today(date_to_convert):
            if R2DateTime.is_within_an_hour(date_to_convert)['status']:
                return R2DateTime.is_within_an_hour(date_to_convert)['text']
            else:
                human_date = ''

        elif R2DateTime.is_yesterday(date_to_convert):
            human_date = 'yesterday at '

        elif R2DateTime.is_same_year(date_to_convert):
            human_date = '%s %s at ' % (human_day, R2DateTime.month_to_string(human_month))

        else:
            human_date = '%s %s %s, ' % (human_day, R2DateTime.month_to_string(human_month), human_year)

        return '%s%s%s' % (human_date, human_time, a_m_p_m)

    @staticmethod
    def is_within_an_hour(date_to_convert):

        # today = datetime.now()

        today = datetime.utcnow().replace(tzinfo=pytz.UTC)

        today = R2DateTime.utc_to_local(today)

        print('\n\n\n\n\nTODAYYY: ' + str(today))

        diff = today - date_to_convert

        if diff.seconds < 60:  # within a min
            return {
                'status': True,
                # 'text':  'just now'
                'text':  '%s seconds ago' % math.floor(diff.seconds)
            }
        elif diff.seconds < 3600:  # within an hour
            calc = math.floor(diff.seconds/60)

            if calc == 1:
                text = 'a minute ago'
            else:
                text = '%s minutes ago' % calc

            return {
                'status': True,
                'text':  text
            }
        else:
            return {
                'status': False
            }

    @staticmethod
    def month_to_string(new_month):

        if new_month is 1:
            month_string = 'Jan'
        elif new_month is 2:
            month_string = 'Feb'
        elif new_month is 3:
            month_string = 'Mar'
        elif new_month is 4:
            month_string = 'Apr'
        elif new_month is 5:
            month_string = 'May'
        elif new_month is 6:
            month_string = 'Jun'
        elif new_month is 7:
            month_string = 'Jul'
        elif new_month is 8:
            month_string = 'Aug'
        elif new_month is 9:
            month_string = 'Sep'
        elif new_month is 10:
            month_string = 'Oct'
        elif new_month is 11:
            month_string = 'Nov'
        else:
            month_string = 'Dec'

        return month_string

    @staticmethod
    def zeroing(num):
        if num < 10:
            zero_string = '0%s' % num
        else:
            zero_string = str(num)
        return zero_string

    @staticmethod
    def is_today(new_date):
        today_bool = False
        today = datetime.now()
        if today.day == new_date.day and today.month == new_date.month and today.year == new_date.year:
            today_bool = True
        return today_bool

    @staticmethod
    def is_yesterday(new_date):
        yester_bool = False
        yesterday = datetime.now()
        if yesterday.day-1 == new_date.day and yesterday.month == new_date.month and yesterday.year == new_date.year:
            yester_bool = True
        return yester_bool

    @staticmethod
    def is_same_year(new_date):
        same_year = False
        dt = datetime.now()
        if new_date.year == dt.year:
            same_year = True
        return same_year

    @staticmethod
    def utc_to_local(utc_datetime):
        now_timestamp = py_time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        return utc_datetime + offset
