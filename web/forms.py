from django.contrib.auth.models import User
from django.forms import Form, CharField, ChoiceField, PasswordInput, ModelForm, IntegerField

from utils.printer import get_printers
from .models import Worker, Category, Food, Room, Table


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
        if position == 'admin':
            admin = True
        else:
            admin = False
        if self.instance is None:
            user = User.objects.create(username=f"{first_name.lower()}_{last_name.lower()}", password=password,
                                       is_staff=admin, is_superuser=admin)
            user.save()
            worker = Worker.objects.create(user=user, first_name=first_name, last_name=last_name, position=position)
            worker.save()
        else:
            self.instance: Worker
            self.instance.user.username = f"{first_name.lower()}_{last_name.lower()}"
            if password != "":
                print("updated")
                self.instance.user.set_password(password)
            self.instance.user.is_superuser = admin
            self.instance.user.is_staff = admin
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
