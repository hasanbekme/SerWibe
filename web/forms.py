from django.contrib.auth.models import User
from django.forms import Form, CharField, ChoiceField, PasswordInput, ModelForm, IntegerField, Textarea

from utils.printer import get_printers
from .models import Worker, Category, Food, Room, Table, ExpenseReason, Expense, Order


class CreateUserForm(Form):
    first_name = CharField()
    last_name = CharField()
    position = ChoiceField(choices=[("waiter", "Offitsant"), ("admin", "Admin")])
    password = CharField(widget=PasswordInput, required=False)

    def __init__(self, *args, instance=None, **kwargs):
        instance: Worker
        super().__init__(*args, **kwargs)
        if instance is not None:
            self.instance: Worker = instance
            self.initial = {
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'position': instance.position,
            }
        else:
            self.instance = None

    def save(self):
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        position = self.cleaned_data.get("position")
        password = self.cleaned_data.get("password")
        if self.instance is None:
            user = User.objects.create(username=f"{first_name.lower()}_{last_name.lower()}", password=password)
            user.save()
            worker = Worker.objects.create(user=user, first_name=first_name, last_name=last_name, position=position)
            worker.save()
        else:
            self.instance: Worker
            self.instance.user.username = f"{first_name.lower()}_{last_name.lower()}"
            if password != "":
                self.instance.user.set_password(password)
            self.instance.first_name = first_name
            self.instance.last_name = last_name
            self.instance.position = position
            self.instance.save()
            self.instance.user.save()


class CategoryForm(ModelForm):
    printer = ChoiceField(choices=[(printer, printer) for printer in get_printers()])

    class Meta:
        model = Category
        fields = '__all__'


class FoodForm(ModelForm):
    class Meta:
        model = Food
        fields = '__all__'


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'


class TableForm(Form):
    number = IntegerField()

    def __init__(self, *args, room=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = room

    def save(self):
        number = self.cleaned_data.get("number")
        table = Table.objects.create(number=number, room=self.room)
        table.save()


class ExpenseReasonForm(ModelForm):
    class Meta:
        model = ExpenseReason
        fields = '__all__'


class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'


class OrderCompletionForm(Form):
    payment_type = ChoiceField(choices=(('cash', 'Naqd'), ('credit_card', 'Kartadan')))
    comment = CharField(widget=Textarea, required=False)

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def save(self):
        payment_type = self.cleaned_data.get('payment_type')
        comment = self.cleaned_data.get('comment')
        self.instance: Order
        if comment is not None:
            self.instance.comment = comment
        self.instance.payment_type = payment_type
        self.instance.is_completed = True
        self.instance.paid_money = self.instance.needed_payment
        self.instance.save()
