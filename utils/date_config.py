import datetime


def get_start_of_week():
    td = datetime.date.today()
    start_date = td - datetime.timedelta(days=td.weekday())
    return start_date
