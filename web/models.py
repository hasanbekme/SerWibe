from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    first_name = models.CharField(max_length=25, verbose_name="Ism")
    last_name = models.CharField(max_length=25, verbose_name="Familiya")
    position = models.CharField(max_length=20, verbose_name="Lavozim", choices=(("waiter", "Offitsant"), ("admin", "Admin")))

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"


class Room(models.Model):
    title = models.CharField(max_length=25, verbose_name="Nomi")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Xona"
        verbose_name_plural = "Xonalar"


class Table(models.Model):
    number = models.IntegerField(verbose_name="Raqami")
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room.title}:{self.number}"

    class Meta:
        verbose_name = "Stol"
        verbose_name_plural = "Stollar"


class Category(models.Model):
    title = models.CharField(max_length=25, verbose_name="Nomi")
    image = models.ImageField(verbose_name="Rasmi", upload_to="categories/", null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'


class Food(models.Model):
    title = models.CharField(max_length=25, verbose_name="Nomi")
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="Rasmi", upload_to="Foods/", null=True)
    price = models.IntegerField(verbose_name="Narxi (so'm)")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Taom'
        verbose_name_plural = 'Taomlar'


class Order(models.Model):
    waiter = models.ForeignKey(to=User, verbose_name="Offitsant", on_delete=models.PROTECT)
    created_at = models.DateTimeField(verbose_name="Sanasi", auto_now_add=True)
    table = models.ForeignKey(to=Table, verbose_name="Stol", on_delete=models.PROTECT)
    is_completed = models.BooleanField(default=False)
    paid_money = models.IntegerField(verbose_name="To'langan summa")

    def __str__(self):
        return str(self.id)

    @property
    def needed_payment(self):
        total = 0
        for item in self.orderitem_set.all():
            total += item.total_price
        return total

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    meal = models.ForeignKey(to=Food, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Soni", default=1)

    @property
    def total_price(self):
        return self.meal.price * self.quantity

    def __str__(self):
        return f"{self.order.id}:{self.id}"
