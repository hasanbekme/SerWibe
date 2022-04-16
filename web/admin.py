from django.contrib import admin

from web.models import *


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    pass


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass
