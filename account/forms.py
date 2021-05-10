from django import forms
from django.contrib.auth.models import User

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    # AGGIUNGI QUESTI DUE CAMPI ALLA FORM CHE VIENE DEFINITA OLTRE A PARTIRE DAL MODELLO USER
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User  # crea la form con i campi di user
        fields = ('username', 'first_name', 'email')  # MA INCLUDI SOLO username first_name e email

    def clean_password2(self):  # clean_nomecampodavalidare
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth','photo')
