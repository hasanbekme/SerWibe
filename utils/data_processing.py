from datetime import datetime, timedelta, date

from django.db.models import Sum

from utils.date_config import get_days_before, get_start_of_the_week, get_start_of_the_month
from web.models import OrderItem, Food, Order, Worker, Category, Table, Expense

today = date.today()
delta = timedelta(days=1)
delta_hour = timedelta(hours=1)


class FoodTrade:
    def __init__(self, trade_data, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pk = instance.pk
        self.title = instance.title
        self.category = instance.category
        self.photo = instance.photo
        self.image = instance.image
        self.price = instance.price
        self.trade_data = trade_data.filter(meal=instance)

    @property
    def total_sale(self):
        res = self.trade_data.aggregate(Sum('paid_amount'))['paid_amount__sum']
        if res is None:
            res = 0
        return res

    @property
    def total_sold(self):
        res = self.trade_data.aggregate(Sum('quantity'))['quantity__sum']
        if res is None:
            res = 0
        return res


def get_trading_table(category=None, start_date=None, end_date=None):
    final_models = OrderItem.objects.all()
    food_models = Food.objects.all()
    if start_date == 'day':
        final_models = final_models.filter(order__created_at__day=today.day, order__created_at__month=today.month,
                                           order__created_at__year=today.year)
        date_string = today.strftime("%a, %d/%m/%Y")
    elif start_date == 'week':
        final_models = final_models.filter(order__created_at__gt=get_days_before(7))
        date_string = f"{get_days_before(7).strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')}"
    elif start_date == 'month':
        final_models = final_models.filter(order__created_at__month=get_days_before(30))
        date_string = f"{get_days_before(30).strftime('01/%m/%Y')} - {today.strftime('%d/%m/%Y')}"
    else:
        if start_date != '' and start_date is not None and end_date != '' and end_date is not None:
            sd = datetime.strptime(start_date, "%Y-%m-%d")
            ed = datetime.strptime(end_date, "%Y-%m-%d")
            final_models = final_models.filter(order__created_at__gt=sd, order__created_at__lt=ed)
            date_string = f"{sd.strftime('01/%m/%Y')} - {ed.strftime('%d/%m/%Y')}"
        else:
            date_string = ""
    if category is not None and category != '':
        food_models = food_models.filter(category_id=category)
        final_models = final_models.filter(meal__category_id=category)

    res = list(map(lambda x: FoodTrade(final_models, x), food_models))
    return res, sum([x.total_sale for x in res]), date_string


class DateInfo:
    def __init__(self, food: Food, _date: date, models):
        self.date = _date.strftime("%d/%m/%Y")
        self.food = food
        self.models = models.filter(order__created_at__day=_date.day, order__created_at__month=_date.month,
                                    order__created_at__year=_date.year)

    @property
    def sale_amount(self):
        res = self.models.aggregate(Sum('paid_amount'))['paid_amount__sum']
        if res is None:
            res = 0
        return res

    @property
    def total_sold(self):
        res = self.models.aggregate(Sum('quantity'))['quantity__sum']
        if res is None:
            res = 0
        return res


class ChartInfo:
    def __init__(self, xvalues, yvalues):
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.mn = min(yvalues) // 2
        self.mx = int(max(yvalues) * 1.1)


def food_trading_data(food, start_date=None, end_date=None):
    start_loop = today - timedelta(days=9)
    end_loop = today + delta

    food = Food.objects.get(id=food)
    final_models = OrderItem.objects.filter(meal=food)

    if start_date in ['week', 'month']:
        end_loop = today + timedelta(days=1)
        if start_date == 'week':
            start_loop = get_days_before(6)
        elif start_date == 'month':
            start_loop = get_days_before(29)
    else:
        if start_date != '' and start_date is not None and end_date != '' and end_date is not None:
            start_loop = datetime.strptime(start_date, "%Y-%m-%d")
            end_loop = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

    query_result = []
    xvalues = []
    yvalues = []

    date_string = f"{start_loop.strftime('%d/%m/%Y')} - {end_loop.strftime('%d/%m/%Y')}"

    while start_loop < end_loop:
        date_info = DateInfo(food, start_loop, final_models)
        xvalues.append(start_loop.strftime("%d/%m"))
        yvalues.append(date_info.sale_amount)
        query_result.append(date_info)
        start_loop += delta

    return reversed(query_result), xvalues, yvalues, food, date_string


class DashboardInfo:
    def __init__(self, food_types, trading, workers, categories, orders, tables, xvalues, yvalues, cash_p,
                 credit_card_p, unpaid_p, date_string):
        self.food_types = food_types
        self.trading = trading
        self.workers = workers
        self.categories = categories
        self.orders = orders
        self.tables = tables
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.cash_p = cash_p
        self.credit_card_p = credit_card_p
        self.unpaid_p = unpaid_p
        self.date_string = date_string


def get_dashboard_info(start_date=None, end_date=None):
    # static data
    food_types = Food.objects.count()
    workers = Worker.objects.filter(position='waiter').count()
    categories = Category.objects.count()
    table_data = Table.objects.all()
    tables = f"{table_data.filter(is_available=False).count()}/{table_data.count()}"
    if start_date in ["", None] or end_date in ["", None]:
        start_date = "today"

    if start_date in ['today', 'week', 'month']:
        end_loop = today + timedelta(days=1)
        if start_date == 'week':
            start_loop = get_start_of_the_week()
        elif start_date == 'month':
            start_loop = get_start_of_the_month()
        else:
            start_loop = datetime(year=today.year, month=today.month, day=today.day, hour=00, minute=00)
            end_loop = datetime.now() + timedelta(seconds=1)
    else:
        if start_date != '' and start_date is not None and end_date != '' and end_date is not None:
            start_loop = datetime.strptime(start_date, "%Y-%m-%d")
            end_loop = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

    xvalues = []
    yvalues = []

    if start_date == "today":
        time_interval = f"Bugun, {start_loop.strftime('%H:%M')} - {end_loop.strftime('%H:%M')}"
    else:
        time_interval = f"{start_loop.strftime('%d/%m/%Y')} - {end_loop.strftime('%d/%m/%Y')}"

    # income statistics
    total_orders = Order.objects.filter(created_at__gt=start_loop, created_at__lt=end_loop)
    orders_count = total_orders.count()
    orders_income = total_orders.aggregate(Sum('paid_money'))['paid_money__sum']
    cash_p = total_orders.aggregate(Sum('cash_money'))['cash_money__sum']
    credit_card_p = total_orders.aggregate(Sum('credit_card'))['credit_card__sum']
    debt_money_p = total_orders.aggregate(Sum('debt_money'))['debt_money__sum']
    if orders_income is None:
        orders_income = 0
    if cash_p is None:
        cash_p = 0
    if credit_card_p is None:
        credit_card_p = 0
    if debt_money_p is None:
        debt_money_p = 0

    if start_date != "today":
        while start_loop < end_loop:
            xvalues.append(start_loop.strftime("%d/%m"))
            sale_amount = total_orders.filter(created_at__year=start_loop.year, created_at__month=start_loop.month,
                                              created_at__day=start_loop.day).aggregate(Sum('paid_money'))[
                'paid_money__sum']
            if sale_amount is None:
                sale_amount = 0
            yvalues.append(sale_amount)
            start_loop += delta
    else:
        xvalues.append("00")
        yvalues.append(0)
        start_loop += delta_hour
        while start_loop < end_loop:
            xvalues.append(start_loop.strftime("%H:%M"))
            sale_amount = \
                total_orders.filter(created_at__gt=(start_loop - timedelta(hours=1)),
                                    created_at__lt=start_loop).aggregate(
                    Sum('paid_money'))['paid_money__sum']
            if sale_amount is None:
                sale_amount = 0
            yvalues.append(sale_amount)
            start_loop += delta_hour
        start_loop = end_loop.replace(minute=0)
        xvalues.append(end_loop.strftime("%H:%M"))
        sale_amount = \
            total_orders.filter(created_at__gt=start_loop,
                                created_at__lt=end_loop).aggregate(
                Sum('paid_money'))['paid_money__sum']
        if sale_amount is None:
            sale_amount = 0
        yvalues.append(sale_amount)

    dashboard = DashboardInfo(food_types, orders_income, workers, categories, orders_count, tables, xvalues, yvalues,
                              cash_p, credit_card_p, debt_money_p, time_interval)

    return dashboard


def get_expenses_data(start_date=None, end_date=None):
    expense_models = Expense.objects.all()
    if start_date == 'today':
        expense_models = expense_models.filter(created_at__day=today.day)
    elif start_date == "week":
        expense_models = expense_models.filter(created_at__gt=get_days_before(6))
    elif start_date == "month":
        expense_models = expense_models.filter(created_at__gt=get_days_before(29))
    else:
        if start_date != '' and start_date is not None and end_date != '' and end_date is not None:
            start_loop = datetime.strptime(start_date, "%Y-%m-%d")
            end_loop = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            expense_models = expense_models.filter(created_at__gt=start_loop, created_at__lt=end_loop)

    return expense_models
