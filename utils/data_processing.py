from datetime import datetime, timedelta, date

from django.db.models import Sum

from utils.date_config import get_start_of_week
from web.models import OrderItem, Food, Order, Worker, Category, Table

today = date.today()
delta = timedelta(days=1)


class FoodTrade(Food):
    def __init__(self, trade_data, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pk = instance.pk
        self.title = instance.title
        self.category = instance.category
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
    if start_date in ['day', 'week', 'month']:
        if start_date == 'day':
            final_models = final_models.filter(order__created_at__day=today.day)
        elif start_date == 'week':
            final_models = final_models.filter(order__created_at__gt=get_start_of_week())
        elif start_date == 'month':
            final_models = final_models.filter(order__created_at__month=today.month)
    else:
        if start_date != '' and start_date is not None:
            final_models = final_models.filter(order__created_at__gt=datetime.strptime(start_date, "%Y-%m-%d"))
        if end_date != '' and end_date is not None:
            final_models = final_models.filter(order__created_at__lt=datetime.strptime(end_date, "%Y-%m-%d"))
    if category is not None and category != '':
        food_models = food_models.filter(category_id=category)
        final_models = final_models.filter(meal__category_id=category)

    res = list(map(lambda x: FoodTrade(final_models, x), food_models))
    return res, sum([x.total_sale for x in res])


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
            start_loop = today - timedelta(days=6)
        elif start_date == 'month':
            start_loop = today - timedelta(days=29)
    else:
        if start_date != '' and start_date is not None and end_date != '' and end_date is not None:
            start_loop = datetime.strptime(start_date, "%Y-%m-%d")
            end_loop = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

    query_result = []
    xvalues = []
    yvalues = []

    while start_loop < end_loop:
        date_info = DateInfo(food, start_loop, final_models)
        xvalues.append(start_loop.strftime("%d/%m"))
        yvalues.append(date_info.sale_amount)
        query_result.append(date_info)
        start_loop += delta

    return reversed(query_result), xvalues, yvalues, food


class DashboardInfo:
    def __init__(self, food_types, trading, workers, categories, orders, tables):
        self.food_types = food_types
        self.trading = trading
        self.workers = workers
        self.categories = categories
        self.orders = orders
        self.tables = tables


def get_dashboard_info():
    food_types = Food.objects.count()
    trading_data = Order.objects.filter(created_at__year=today.year, created_at__month=today.month,
                                        created_at__day=today.day)
    trading = trading_data.aggregate(Sum('paid_money'))['paid_money__sum']
    if trading is None:
        trading = 0
    workers = Worker.objects.filter(position='waiter').count()
    categories = Category.objects.count()
    orders = f"{trading_data.filter(is_completed=False).count()}/{trading_data.count()}"
    table_data = Table.objects.all()
    tables = f"{table_data.filter(is_available=False).count()}/{table_data.count()}"
    dashboard_info = DashboardInfo(food_types, trading, workers, categories, orders, tables)
    return dashboard_info


def get_sales_graph_data(start_date=None, end_date=None):
    start_loop = today - timedelta(days=9)
    end_loop = today + delta

    order_models = Order.objects.all()

    if start_date in ['week', 'month']:
        end_loop = today + timedelta(days=1)
        if start_date == 'week':
            start_loop = today - timedelta(days=6)
        elif start_date == 'month':
            start_loop = today - timedelta(days=29)
    else:
        if start_date != '' and start_date is not None and end_date != '' and end_date is not None:
            start_loop = datetime.strptime(start_date, "%Y-%m-%d")
            end_loop = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

    xvalues = []
    yvalues = []

    while start_loop < end_loop:
        xvalues.append(start_loop.strftime("%d/%m"))
        sale_amount = order_models.filter(created_at__year=start_loop.year, created_at__month=start_loop.month,
                                          created_at__day=start_loop.day).aggregate(Sum('paid_money'))['paid_money__sum']
        if sale_amount is None:
            sale_amount = 0
        yvalues.append(sale_amount)
        start_loop += delta

    return xvalues, yvalues
