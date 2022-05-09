from utils.payment_receipt import printer_order_item
from web.models import Food, Table, Worker, Order, OrderItem


def get_user(request):
    result = Worker.objects.get(user=request.user)
    return result


def is_admin(request):
    user = get_user(request)
    if user.position == 'admin':
        return True
    else:
        return False


def is_waiter(request):
    user = get_user(request)
    if user.position == 'waiter':
        return True
    else:
        return False


def order_items_add(post_data: dict, table_model: Table, waiter: Worker):
    if table_model.is_available:
        current_order = Order.objects.create(waiter=waiter, table=table_model)
        table_model.is_available = False
        table_model.save()
    else:
        current_order = table_model.current_order
    food_objects = Food.objects.filter(is_available=True, category__is_available=True)
    for food in food_objects:
        quantity = post_data[str(food.id)]
        if quantity != '':
            new_order_item = OrderItem.objects.create(order=current_order, meal=food, quantity=int(quantity))
            new_order_item.save()
            if food.category.printing_required:
                printer_order_item(new_order_item)
    current_order.save()


def pickup_items_add(post_data: dict, staff: Worker):
    new_order = Order.objects.create(waiter=staff, order_type='pickup')
    food_objects = Food.objects.filter(is_available=True, category__is_available=True)
    for food in food_objects:
        quantity = post_data[str(food.id)]
        if quantity != '':
            new_order_item = OrderItem.objects.create(order=new_order, meal=food, quantity=int(quantity))
            new_order_item.save()
            if food.category.printing_required:
                printer_order_item(new_order_item)
    new_order.save()
