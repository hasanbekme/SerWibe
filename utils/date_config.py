import datetime

today = datetime.date.today()


def get_days_before(days):
    start_date = today - datetime.timedelta(days=days)
    return start_date


def get_start_of_the_week():
    return today - datetime.timedelta(days=today.weekday())


def get_start_of_the_month():
    return today - datetime.timedelta(days=(today.day - 1))
