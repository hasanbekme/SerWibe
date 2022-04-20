from django.contrib.auth.forms import UserCreationForm

from .models import Worker
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Worker


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class ProfileForm(ModelForm):
    class Meta:
        model = Worker
        fields = ('first_name', 'last_name', 'position')
