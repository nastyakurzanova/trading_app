from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserAPIKey, TradingSettings

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'middle_name', 'mobile', 'password1', 'password2']

class TradingSettingsForm(forms.ModelForm):
    CURRENCY_CHOICES = [
        ('USD', 'USD - Доллар США'),
        ('EUR', 'EUR - Евро'),
        ('RUB', 'RUB - Рубль'),
        ('GBP', 'GBP - Фунт стерлингов'),
        ('JPY', 'JPY - Йена'),
    ]
    
    LEVERAGE_CHOICES = [
        (1, '1:1 (без плеча)'),
        (2, '1:2'),
        (5, '1:5'),
        (10, '1:10'),
        (20, '1:20'),
        (50, '1:50'),
        (100, '1:100'),
    ]
    
    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Валюта торговли'
    )
    
    leverage = forms.ChoiceField(
        choices=LEVERAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Кредитное плечо'
    )

    class Meta:
        model = TradingSettings
        fields = ['margin_type', 'currency', 'leverage', 'deposit_percent']
        labels = {
            'margin_type': 'Вид маржи',
            'deposit_percent': 'Торгуемый % депозита',
        }
        widgets = {
            'margin_type': forms.Select(attrs={'class': 'form-select'}),
            'deposit_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        }

class APIKeyForm(forms.ModelForm):
    class Meta:
        model = UserAPIKey
        fields = ['api_key', 'secret_key']
        widgets = {
            'api_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите API Key'}),
            'secret_key': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите Secret Key'}),
        }