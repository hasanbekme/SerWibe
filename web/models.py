import datetime

from PIL import Image
from django.contrib.auth.models import User
from django.db import models

from utils.system_settings import get_tax


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    first_name = models.CharField(max_length=25, verbose_name="Ism")
    last_name = models.CharField(max_length=25, verbose_name="Familiya")
    position = models.CharField(max_length=20, verbose_name="Lavozim",
                                choices=(("waiter", "Offitsant"), ("admin", "Admin")))

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

    def save(self, *args, **kwargs):
        super(Worker, self).save()
        if self.position == "admin":
            self.user.is_superuser = True
            self.user.is_staff = True
        else:
            self.user.is_superuser = False
            self.user.is_staff = False
        self.user.save()

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        ordering = ['position']
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"


class Room(models.Model):
    title = models.CharField(max_length=25, verbose_name="Nomi")

    def __str__(self):
        return self.title

    @property
    def tables_count(self):
        return self.table_set.count()

    @property
    def busy_tables(self):
        return self.table_set.filter(is_available=False).count()

    class Meta:
        ordering = ['title']
        verbose_name = "Xona"
        verbose_name_plural = "Xonalar"


class Table(models.Model):
    number = models.IntegerField(verbose_name="Raqami")
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    tax_required = models.BooleanField(default=True)
    service_cost = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room.title}:{self.number}"

    @property
    def current_order(self):
        return self.order_set.filter(is_completed=False).last()

    class Meta:
        ordering = ['number']
        verbose_name = "Stol"
        verbose_name_plural = "Stollar"


class Category(models.Model):
    title = models.CharField(max_length=25, verbose_name="Nomi")
    image = models.ImageField(verbose_name="Rasmi", upload_to="categories/", null=True, blank=True)
    is_available = models.BooleanField(default=True)
    printing_required = models.BooleanField(default=False)
    printer = models.CharField(max_length=250, verbose_name="Printer",
                               blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def photo(self):
        if self.image:
            return self.image.url
        else:
            return "/static/img/default_image.png"

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        imag = Image.open(self.image.path)
        output_size = (70, 70)
        imag.thumbnail(output_size)
        imag.save(self.image.path)

    class Meta:
        ordering = ['title']
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'


class Food(models.Model):
    title = models.CharField(max_length=25, verbose_name="Nomi")
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="Rasmi", upload_to="Foods/", null=True, blank=True)
    price = models.IntegerField(verbose_name="Narxi (so'm)")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def photo(self):
        if self.image:
            return self.image.url
        else:
            return "/static/img/default_image.png"

    def save(self, *args, **kwargs):
        super(Food, self).save(*args, **kwargs)
        imag = Image.open(self.image.path)
        output_size = (70, 70)
        imag.thumbnail(output_size)
        imag.save(self.image.path)

    class Meta:
        ordering = ['title']
        verbose_name = 'Taom'
        verbose_name_plural = 'Taomlar'


class Order(models.Model):
    waiter = models.ForeignKey(to=Worker, verbose_name="Offitsant", on_delete=models.PROTECT)
    created_at = models.DateTimeField(verbose_name="Sanasi", auto_now_add=True)
    order_type = models.CharField(max_length=25, choices=(('table', 'Stol'), ('pickup', 'Olib ketish')),
                                  default='table')
    table = models.ForeignKey(to=Table, verbose_name="Stol", on_delete=models.PROTECT, null=True)
    is_completed = models.BooleanField(default=False)
    paid_money = models.IntegerField(verbose_name="To'langan summa", null=True, blank=True)
    cash_money = models.IntegerField(default=0)
    credit_card = models.IntegerField(default=0)
    debt_money = models.IntegerField(default=0)
    comment = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def passed_time(self):
        return self.created_at - datetime.datetime.now()

    @property
    def service_cost(self):
        return (self.table.service_cost * self.passed_time.total_seconds() // 360000) * 100

    @property
    def needed_payment(self):
        total = 0
        for item in self.orderitem_set.all():
            total += item.paid_amount
        return total

    @property
    def without_tax(self):
        total = 0
        for item in self.orderitem_set.all():
            total += item.abstract_amount
        return total

    @property
    def tax_price(self):
        return self.paid_money - self.without_tax

    @property
    def created_time(self):
        return self.created_at.strftime("%d/%m/%Y, %H:%M")

    class Meta:
        ordering = ['-id']
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    meal = models.ForeignKey(to=Food, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Soni", default=1)
    paid_amount = models.IntegerField(null=True)
    abstract_amount = models.IntegerField(null=True)

    @property
    def total_price(self):
        if self.order.order_type == 'table':
            if self.order.table.tax_required:
                return int(self.meal.price * self.quantity * (1 + get_tax() / 100))
            else:
                return int(self.meal.price * self.quantity) + self.order.service_cost
        else:
            return int(self.meal.price * self.quantity)

    def __str__(self):
        return f"{self.order.id}:{self.id}"

    def save(self, *args, **kwargs):
        super(OrderItem, self).save()
        self.paid_amount = self.total_price
        self.abstract_amount = int(self.meal.price * self.quantity)

    class Meta:
        ordering = ['-id']


class ExpenseReason(models.Model):
    title = models.CharField(max_length=50, verbose_name='Nomi')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Expense(models.Model):
    reason = models.ForeignKey(to=ExpenseReason, on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="Sanasi", auto_now_add=True)
    performer = models.ForeignKey(to=Worker, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name="Sarflangan summa")

    @property
    def created_time(self):
        return self.created_at.strftime("%d/%m/%Y, %H:%M")

    class Meta:
        ordering = ['-id']
