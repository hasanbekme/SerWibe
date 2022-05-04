from web.models import Food


def order_items_add(post_data):
    food_objects = Food.objects.filter(is_available=True, category__is_available=True)
    for food in food_objects:
        quantity = post_data[str(food.id)]
        if quantity != '':
            print(food.title, ': ', quantity)
