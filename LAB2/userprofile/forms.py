from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from models import CustomUser

# Our custom registration form. Easily modifiable.
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    birthday = forms.DateField(required=False)
    # extra = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_password1(self):
        password = self.cleaned_data['password1']
        if len(password) < 8:
            raise ValidationError('Password needs to contain at least 8 characters.')
        return password

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.birthday = self.cleaned_data['birthday']

        if commit:
            user.save()

        new = CustomUser(user=user)
        new.save()

# Wrapper around Django's default authentication form. For possible future changes.
class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        # fields = ('username', 'password')
        
    def clean(self):
        cleaned_data = super(UserLoginForm, self).clean()
        return cleaned_data
