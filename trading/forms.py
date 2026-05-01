from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, UserAPIKey, TradingSettings


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'})
    )
    first_name = forms.CharField(
        label='Имя',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'})
    )
    middle_name = forms.CharField(
        label='Отчество',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите отчество'})
    )
    mobile = forms.CharField(
        label='Телефон',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'})
    )
    username = forms.CharField(
        label='Логин',
        help_text='Не более 150 символов. Только буквы, цифры и @/./+/-/_.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте логин'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте пароль'}),
        help_text='Пароль должен содержать минимум 8 символов, не должен быть простым или состоять только из цифр.'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}),
        help_text='Введите тот же пароль для подтверждения.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'middle_name', 'mobile', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )

    error_messages = {
        'invalid_login': 'Неверный логин или пароль. Проверьте данные.',
        'inactive': 'Эта учётная запись отключена.',
    }


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