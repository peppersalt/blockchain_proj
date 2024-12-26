# forms.py
from django import forms

class WalletForm(forms.Form):
    username = forms.CharField(max_length=255, label="Логин")
    password = forms.CharField(max_length=255, label="Пароль", widget=forms.PasswordInput)
