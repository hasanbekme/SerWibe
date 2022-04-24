from django.contrib.auth.models import User
from django.forms import Form, CharField, ChoiceField, PasswordInput, ModelForm, \
    ModelChoiceField, IntegerField

from utils.printer import get_printers
from .models import Worker, Category, Food


class CreateUserForm(Form):
    first_name = CharField()
    last_name = CharField()
    position = ChoiceField(choices=[("waiter", "Offitsant"), ("admin", "Admin")])
    password = CharField(widget=PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self):
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        position = self.cleaned_data.get("position")
        password = self.cleaned_data.get("password")
        if position == 'admin':
            admin = True
        else:
            admin = False
        user = User.objects.create(username=f"{first_name.lower()}_{last_name.lower()}", password=password,
                                   is_staff=admin, is_superuser=admin)
        user.save()
        worker = Worker.objects.create(user=user, first_name=first_name, last_name=last_name, position=position)
        worker.save()


class CategoryForm(ModelForm):
    printer = ChoiceField(choices=[(printer, printer) for printer in get_printers()])

    class Meta:
        model = Category
        fields = '__all__'


class FoodForm(ModelForm):
    class Meta:
        model = Food
        fields = '__all__'
