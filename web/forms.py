from django.db.models import fields
from .models import Worker
from django import forms
from django.forms import ModelForm
from django import forms


from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class ProfileForm(ModelForm):
    class Meta:
        model = Worker
        fields = ('first_name', 'last_name', 'position')