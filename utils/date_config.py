import datetime

today = datetime.date.today()


def get_days_before(days):
    start_date = today - datetime.timedelta(days=days)
    return start_date
