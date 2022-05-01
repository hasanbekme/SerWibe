from datetime import datetime

from django.db.models import Sum

from utils.date_config import get_start_of_week
from web.models import OrderItem, Food


class FoodTrade(Food):
    def __init__(self, trade_data, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    today = datetime.today()
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
    return res
