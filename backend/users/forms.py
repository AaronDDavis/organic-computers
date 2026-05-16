from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import TextInput, EmailInput, Select
from . import models

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = models.User
        
        fields = ('email', 'first_name', 'last_name', 'username', 'password1', 'password2', 'role')

        widgets = {
            'email': EmailInput(),
            'first_name': TextInput(),
            'last_name': TextInput(),
            'username': TextInput(),
            'role': Select(),
        }


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

