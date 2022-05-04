from utils.payment_receipt import printer_order_item
from web.models import Food, Table, Worker, Order, OrderItem


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
