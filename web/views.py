import json
from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404, reverse

from utils.data_processing import get_trading_table, food_trading_data, get_dashboard_info, get_sales_graph_data
from utils.date_config import get_start_of_week
from utils.payment_receipt import print_receipt
from utils.request_processing import get_user, is_waiter, is_admin
from utils.request_processing import order_items_add
from utils.system_settings import get_tax
from .forms import CreateUserForm, CategoryForm, FoodForm, RoomForm, TableForm, ExpenseReasonForm, ExpenseForm, \
    OrderCompletionForm
from .models import Worker, Category, Food, Room, Table, Order, Expense, ExpenseReason, OrderItem


# authentication views -------------------------------------------------------------------------------------------------
def logoutUser(request):
    logout(request)
    return redirect('signin')


def signin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        waiters = Worker.objects.filter(position="waiter")
        admins = Worker.objects.filter(position="admin")
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.worker.position == 'admin':
                    login(request, user)
                    return redirect('dashboard')
                elif user.worker.position == "waiter":
                    login(request, user)
                    return redirect('room')
            else:
                messages.error(request, "Xato! Parol noto`g`ri")
                return redirect('signin')
        context = {"waiters": waiters, "admins": admins}
        return render(request, 'login.html', context)


# ----------------------------------------------------------------------------------------------------------------------


# admin views
# dashboard ------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def dashboard(request):
    user = get_user(request)
    if is_admin(request):
        start_date = request.GET.get('fir')
        end_date = request.GET.get('sec')
        dashboard_info = get_dashboard_info()
        xvalues, yvalues, date_string = get_sales_graph_data(start_date, end_date)
        mx = int(max(yvalues) * 1.1)
        mn = min(yvalues) // 2
        return render(request, 'dashboard.html',
                      {'dashboard_info': dashboard_info, 'labels': json.dumps(xvalues), 'data': json.dumps(yvalues),
                       'mx': mx, 'mn': mn, 'date_string': json.dumps(date_string)})
    else:
        return redirect('room')


# ----------------------------------------------------------------------------------------------------------------------


# active orders views --------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def orders(request):
    if is_admin(request):
        order_models = Order.objects.filter(is_completed=False)
        return render(request, 'orders/orders.html', context={'orders': order_models})
    else:
        return redirect('room')


@login_required(login_url='/')
def order_view(request, pk):
    if is_admin(request):
        order_model = get_object_or_404(Order, pk=pk)
        order_items = order_model.orderitem_set.all()
        return render(request, 'orders/order_view.html',
                      context={'order': order_model, 'orderitems': order_items, 'tax': get_tax()})
    else:
        return redirect('room')


@login_required(login_url='/')
def print_order(request, order_id):
    if is_admin(request):
        order_model = get_object_or_404(Order, id=order_id)
        print_receipt(order=order_model)
        return redirect('orders')
    else:
        return redirect('room')


@login_required(login_url='/')
def complete_order(request, pk):
    if is_admin(request):
        order = get_object_or_404(Order, pk=pk)
        order_items = order.orderitem_set.all()
        if request.method == "POST":
            form = OrderCompletionForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect('orders')
        else:
            form = OrderCompletionForm()
        return render(request, "orders/complete_order.html",
                      context={'form': form, 'order': order, 'orderitems': order_items})
    else:
        return redirect('room')


# ----------------------------------------------------------------------------------------------------------------------


# staffs views ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def worker(request):
    if is_admin(request):
        workers = Worker.objects.all()
        context = {'workers': workers}
        return render(request, 'workers/worker.html', context)
    else:
        return redirect('room')


@login_required(login_url='/')
def user_new(request):
    if is_admin(request):
        if request.method == "POST":
            form = CreateUserForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('worker')
            else:
                print(form.errors)
        else:
            form = CreateUserForm()
        return render(request, 'workers/user_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def user_edit(request, pk):
    if is_admin(request):
        post = get_object_or_404(Worker, pk=pk)
        if request.method == "POST":
            form = CreateUserForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('worker')
        else:
            form = CreateUserForm(instance=post)
        return render(request, 'workers/user_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def user_delete(request, pk):
    if is_admin(request):
        obj = get_object_or_404(Worker, pk=pk)

        if request.method == "POST":
            obj.user.delete()
            obj.delete()
            return redirect('worker')

        return render(request, "workers/user_delete.html", {'user': obj})
    else:
        return redirect('room')


# ----------------------------------------------------------------------------------------------------------------------


# meal types -----------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def product(request):
    if is_admin(request):
        category_id = request.GET.get('category')
        categories = Category.objects.all()
        if category_id is not None:
            foods = Food.objects.filter(category_id=int(category_id))
        else:
            foods = Food.objects.all()
        p = Paginator(foods, 10)
        page = p.get_page(request.GET.get('page'))
        context = {'categories': categories, 'foods': page, 'p_paginator': page}
        return render(request, 'foods/product.html', context)
    else:
        return redirect('room')


@login_required(login_url='/')
def category_edit(request, pk):
    if is_admin(request):
        post = get_object_or_404(Category, pk=pk)
        if request.method == "POST":
            form = CategoryForm(request.POST, instance=post)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('product') + '#C')
        else:
            form = CategoryForm(instance=post)
        return render(request, 'foods/category_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def category_new(request):
    if is_admin(request):
        if request.method == "POST":
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('product') + '#C')
            else:
                print(form.errors)
        else:
            form = CategoryForm()
        return render(request, 'foods/category_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def category_delete(request, pk):
    if is_admin(request):
        obj = get_object_or_404(Category, pk=pk)

        if request.method == "POST":
            obj.delete()
            return redirect(reverse('product') + '#C')

        return render(request, "foods/category_delete.html", {'category': obj})
    else:
        return redirect('room')


@login_required(login_url='/')
def food_edit(request, pk):
    if is_admin(request):
        food = get_object_or_404(Food, pk=pk)
        if request.method == "POST":
            form = FoodForm(request.POST, instance=food)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect('product')
        else:
            form = FoodForm(instance=food)
        return render(request, 'foods/food_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def food_new(request):
    if is_admin(request):
        if request.method == "POST":
            form = FoodForm(request.POST, request.FILES)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect('product')
            else:
                print(form.errors)
        else:
            form = FoodForm()
        return render(request, 'foods/food_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def food_delete(request, pk):
    if is_admin(request):
        obj = get_object_or_404(Food, pk=pk)

        if request.method == "POST":
            obj.delete()
            return redirect('product')

        return render(request, "foods/food_delete.html", {'food': obj})
    else:
        return redirect('room')


# ----------------------------------------------------------------------------------------------------------------------


# tables manager in admin views ----------------------------------------------------------------------------------------
@login_required(login_url='/')
def rooms(request):
    if is_admin(request):
        room_models = Room.objects.all()
        p = Paginator(room_models, 10)
        page = p.get_page(request.GET.get('page'))
        context = {'rooms': page, 'p_paginator': page}
        return render(request, 'tables/rooms.html', context)
    else:
        return redirect('room')


@login_required(login_url='/')
def room_new(request):
    if is_admin(request):
        if request.method == "POST":
            form = RoomForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect('rooms')
            else:
                print(form.errors)
        else:
            form = RoomForm()
        return render(request, 'tables/room_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def room_tables(request, pk):
    if is_admin(request):
        rm = get_object_or_404(Room, pk=pk)
        tables = rm.table_set.all()
        return render(request, 'tables/room_tables.html', {'tables': tables, 'room': rm})
    else:
        return redirect('room')


@login_required(login_url='/')
def room_edit(request, pk):
    if is_admin(request):
        room_model = get_object_or_404(Room, pk=pk)
        if request.method == "POST":
            form = RoomForm(request.POST, instance=room_model)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect('rooms')
        else:
            form = RoomForm(instance=room_model)
        return render(request, 'tables/room_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def room_delete(request, pk):
    if is_admin(request):
        obj = get_object_or_404(Room, pk=pk)

        if request.method == "POST":
            obj.delete()
            return redirect('rooms')

        return render(request, "tables/room_delete.html", {'food': obj})
    else:
        return redirect('room')


@login_required(login_url='/')
def table_new(request, pk):
    if is_admin(request):
        room_m = get_object_or_404(Room, pk=pk)
        if request.method == "POST":
            form = TableForm(request.POST, room=room_m)
            if form.is_valid():
                form.save()
                return redirect('room_tables', pk=pk)
            else:
                print(form.errors)
        else:
            form = TableForm()
        return render(request, 'tables/table_add.html', {'form': form, 'room': room_m})
    else:
        return redirect('room')


@login_required(login_url='/')
def table_delete(request, pk_room, pk_table):
    if is_admin(request):
        room_obj = get_object_or_404(Room, pk=pk_room)
        table_obj = get_object_or_404(Table, pk=pk_table)

        if request.method == "POST":
            table_obj.delete()
            return redirect('room_tables', pk=pk_room)

        return render(request, "tables/table_delete.html", {'room': room_obj, 'table': table_obj})
    else:
        return redirect('room')


# ----------------------------------------------------------------------------------------------------------------------


# expenses manager views -----------------------------------------------------------------------------------------------
@login_required(login_url='/')
def expenses(request):
    if is_admin(request):
        dt = request.GET.get('date')
        today = datetime.today()
        if dt == 'today':
            expense_models = Expense.objects.filter(created_at__day=today.day)
        elif dt == "week":
            expense_models = Expense.objects.filter(created_at__gt=get_start_of_week())
        elif dt == "month":
            expense_models = Expense.objects.filter(created_at__month=today.month)
        else:
            expense_models = Expense.objects.all()
        p = Paginator(expense_models, 8)
        page = p.get_page(request.GET.get('page'))
        expense_reason_models = ExpenseReason.objects.all()
        return render(request, 'expenses/expenses.html',
                      context={'expenses': page, 'expense_reasons': expense_reason_models, 'p_paginator': page})
    else:
        redirect('room')


@login_required(login_url='/')
def expense_reason_new(request):
    if is_admin(request):
        if request.method == "POST":
            form = ExpenseReasonForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('expenses') + '#C')
            else:
                print(form.errors)
        else:
            form = ExpenseReasonForm()
        return render(request, 'expenses/expense_reason_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def expense_reason_edit(request, pk):
    if is_admin(request):
        expense_reason = get_object_or_404(ExpenseReason, pk=pk)
        if request.method == "POST":
            form = ExpenseReasonForm(request.POST, instance=expense_reason)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('expenses') + '#C')
        else:
            form = ExpenseReasonForm(instance=expense_reason)
        return render(request, 'expenses/expense_reason_edit.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def expense_new(request):
    if is_admin(request):
        worker_model = Worker.objects.get(user=request.user)
        if request.method == "POST":
            tempt_dict = request.POST.copy()
            tempt_dict['performer'] = str(worker_model.id)
            form = ExpenseForm(tempt_dict)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('expenses'))
            else:
                print(form.errors)
        else:
            default_choice = request.GET.get('reason')
            if default_choice is not None:
                form = ExpenseForm(initial={'reason': ExpenseReason.objects.get(id=int(default_choice))})
            else:
                form = ExpenseForm()
        return render(request, 'expenses/expense_new.html', {'form': form})
    else:
        return redirect('room')


@login_required(login_url='/')
def expense_delete(request, pk):
    if is_admin(request):
        expense_model = get_object_or_404(Expense, pk=pk)
        if request.method == "POST":
            expense_model.delete()
            return redirect('expenses')

        return render(request, "expenses/expense_delete.html")
    else:
        return redirect('room')


@login_required(login_url='/')
def expense_reason_delete(request, pk):
    if is_admin(request):
        expense_reason_model = get_object_or_404(ExpenseReason, pk=pk)
        if request.method == "POST":
            expense_reason_model.delete()
            return redirect('expenses')

        return render(request, "expenses/expense_reason_delete.html", {'reason': expense_reason_model})
    else:
        return redirect('room')


# ----------------------------------------------------------------------------------------------------------------------


# trading views --------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def trading(request):
    if is_admin(request):
        category_models = Category.objects.all()
        category_parameter = request.GET.get('category')
        start_date = request.GET.get('fir')
        end_date = request.GET.get('sec')
        food_data, total_sum, date_string = get_trading_table(category_parameter, start_date, end_date)
        p = Paginator(food_data, 10)
        page = p.get_page(request.GET.get('page'))
        return render(request, 'trading/income.html',
                      {'foods': page, 'categories': category_models, 'total': total_sum, 'date_string': date_string,
                       'p_paginator': page})
    else:
        return redirect('room')


@login_required(login_url='/')
def trading_detailed_view(request, pk):
    if is_admin(request):
        start_date = request.GET.get('fir')
        end_date = request.GET.get('sec')
        dates, xvalues, yvalues, food_model, date_string = food_trading_data(pk, start_date, end_date)
        mn = min(yvalues) // 2
        mx = int(max(yvalues) * 1.1)
        return render(request, 'trading/detailed_view.html',
                      {'dates': dates, 'labels': json.dumps(xvalues), 'data': json.dumps(yvalues), 'mn': mn, 'mx': mx,
                       'food': food_model,
                       'total': sum(yvalues), 'date_string': json.dumps(date_string)})
    else:
        return redirect('room')


# ----------------------------------------------------------------------------------------------------------------------


# archive manager views ------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def archive(request):
    if is_admin(request):
        now = datetime.now()
        waiter_models = Worker.objects.filter(position='waiter')
        order_models = Order.objects.filter(is_completed=True)
        fir = request.GET.get('fir')
        sec = request.GET.get('sec')
        waiter = request.GET.get('waiter')
        date_string = ""
        if fir in ['day', 'week', 'month']:
            if fir == 'day':
                order_models = order_models.filter(created_at__day=now.day)
                date_string = now.strftime("%a, %d/%m/%Y")
            elif fir == 'week':
                order_models = order_models.filter(created_at__gt=get_start_of_week())
                date_string = f"{get_start_of_week().strftime('%d/%m/%Y')} - {now.strftime('%d/%m/%Y')}"
            elif fir == 'month':
                order_models = order_models.filter(created_at__month=now.month)
                date_string = f"{get_start_of_week().strftime('01/%m/%Y')} - {now.strftime('%d/%m/%Y')}"
        else:
            if fir != '' and fir is not None and sec != '' and sec is not None:
                sd = datetime.strptime(fir, "%Y-%m-%d")
                ed = datetime.strptime(sec, "%Y-%m-%d")
                order_models = order_models.filter(created_at__gt=sd, created_at__lt=ed)
                date_string = f"{sd.strftime('01/%m/%Y')} - {ed.strftime('%d/%m/%Y')}"
        if waiter not in [None, '']:
            order_models = order_models.filter(waiter_id=int(waiter))
        total_sum = order_models.aggregate(Sum('paid_money'))['paid_money__sum']
        if total_sum is None:
            total_sum = 0
        p = Paginator(order_models, 10)
        page = p.get_page(request.GET.get('page'))
        return render(request, "archive/archive.html",
                      context={'waiters': waiter_models, 'orders': page, 'date_string': date_string,
                               'total_sum': total_sum,
                               'p_paginator': page,
                               'tax': get_tax()})
    else:
        return redirect('room')


@login_required(login_url='/')
def archive_order_view(request, pk):
    if is_admin(request):
        order_model = get_object_or_404(Order, pk=pk)
        order_items = order_model.orderitem_set.all()
        return render(request, 'archive/order_view.html', context={'order': order_model, 'orderitems': order_items})
    else:
        return redirect('room')


# ----------------------------------------------------------------------------------------------------------------------


# waiter views ---------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def room(request):
    if is_waiter(request):
        room_models = Room.objects.all()
        return render(request, 'waiter/room.html', {'rooms': room_models})
    else:
        return redirect('dashboard')


@login_required(login_url='/')
def table(request, pk):
    if is_waiter(request):
        user = get_user(request)
        room_model = get_object_or_404(Room, pk=pk)
        tables = room_model.table_set.all()
        busy_tables = tables.filter(is_available=False).count()
        return render(request, 'waiter/tables.html',
                      {'tables': tables, 'room': room_model, 'busy_tables': busy_tables, 'waiter': user})
    else:
        return redirect('dashboard')


@login_required(login_url='/')
def add_item(request, pk_room, pk_table):
    if is_waiter(request):
        room_model = Room.objects.get(pk=pk_room)
        table_model = Table.objects.get(pk=pk_table)
        waiter = Worker.objects.get(user=request.user)
        if request.method == 'POST':
            order_items_add(request.POST, table_model, waiter)
        else:
            food_models = Food.objects.filter(is_available=True, category__is_available=True)
            category_models = Category.objects.filter(is_available=True)
            return render(request, 'waiter/add_item.html',
                          {"foods": food_models, 'categories': category_models, 'table': table_model,
                           'room': room_model})
        return redirect('my_orders')
    else:
        return redirect('dashboard')


@login_required(login_url='/')
def waiter_order(request, pk):
    if is_waiter(request):
        table_model = get_object_or_404(Table, pk=pk)
        order_model = table_model.current_order
        return render(request, 'waiter/order_view.html',
                      {'room': table_model.room, 'table': table_model, 'orderitems': order_model.orderitem_set.all(),
                       'order': order_model})
    else:
        return redirect('dashboard')


@login_required(login_url='/')
def order_item_delete(request, pk):
    if is_waiter(request):
        order_item = get_object_or_404(OrderItem, pk=pk)
        order_model = order_item.order
        order_item.delete()
        return redirect('waiter_order', pk=order_model.table.pk)
    else:
        return redirect('dashboard')


@login_required(login_url='/')
def print_order_receipt(request, order_id):
    if is_waiter(request):
        order_model = get_object_or_404(Order, id=order_id)
        print_receipt(order=order_model)
        return redirect('waiter_order', pk=order_model.table.pk)
    else:
        return redirect('dashboard')


@login_required(login_url='/')
def my_orders(request):
    if is_waiter(request):
        user = get_user(request)
        current_orders = Order.objects.filter(waiter=user, is_completed=False)
        print(current_orders)
        return render(request, 'waiter/my_orders.html', {'orders': current_orders})
    else:
        return redirect('dashboard')


@login_required(login_url='/')
def my_profile(request):
    if is_waiter(request):
        user = get_user(request)
        today = date.today()
        order_models = Order.objects.filter(waiter=user, created_at__gt=today)
        orders_amount = order_models.aggregate(Sum('paid_money'))['paid_money__sum']
        if orders_amount is None:
            orders_amount = 0
        return render(request, 'waiter/my_profile.html',
                      {'user': user, 'orders_count': order_models.count(), 'orders_amount': orders_amount})
    else:
        return redirect('dashboard')


# ----------------------------------------------------------------------------------------------------------------------

@login_required(login_url='/')
def pickup(request):
    if is_admin(request):
        order_models = Order.objects.filter(is_completed=False, order_type="pickup")
        return render(request, 'pickup/pickup.html', {"orders": order_models})
    else:
        return redirect("room")


@login_required(login_url='/')
def pickup_add(request):
    if is_admin(request):
        staff = Worker.objects.get(user=request.user)
        if request.method == 'POST':
            order_items_add(request.POST, staff)
        else:
            food_models = Food.objects.filter(is_available=True, category__is_available=True)
            category_models = Category.objects.filter(is_available=True)
            return render(request, 'pickup/pickup_add.html',
                          {"foods": food_models, 'categories': category_models})
        return redirect('pickup')
    else:
        return redirect('room')
