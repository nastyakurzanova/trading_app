# trading/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Расширяем стандартную модель пользователя Django
class User(AbstractUser):
    middle_name = models.CharField(max_length=150, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    intro = models.TextField(blank=True)
    profile = models.TextField(blank=True)
    modified_at = models.DateTimeField(auto_now=True)
    # Поля first_name, last_name, email, password, last_login, date_joined уже есть в AbstractUser

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

class StockItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название актива")
    full_name = models.CharField(max_length=300, blank=True, verbose_name="Полное название")
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Мета-заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL-slug")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    currency = models.CharField(max_length=10, default='RUB', verbose_name="Валюта")
    open_price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name="Цена открытия")
    close_price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name="Цена закрытия")
    description = models.TextField(blank=True, verbose_name="Описание")
    sector = models.CharField(max_length=100, blank=True, verbose_name="Сектор")
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Капитализация")
    dividend_yield = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Див. доходность")
    sale_at = models.DateTimeField(null=True, blank=True, verbose_name="Время продажи")
    buy_at = models.DateTimeField(null=True, blank=True, verbose_name="Время покупки")

    def __str__(self):
        return self.title
    
    def get_change_percent(self):
        if self.open_price and self.close_price:
            change = (self.close_price - self.open_price) / self.open_price * 100
            return round(change, 2)
        return 0

# Модель для портфеля пользователя
class StockPortfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

# Модель для хранения API-ключей пользователя (функциональный блок 2)
class UserAPIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

# Модель для платежей
class UserPay(models.Model):
    PAYMENT_TYPES = [
        ('card', 'Банковская карта'),
        ('crypto', 'Криптовалюта'),
        ('bank', 'Банковский перевод'),
        ('qiwi', 'Электронные кошельки'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name="Тип платежа")
    acquiring = models.CharField(max_length=100, verbose_name="Платёжная система")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время платежа")

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.get_payment_type_display()})"

class TradingSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trading_settings')
    margin_type = models.CharField(
        max_length=20,
        choices=[('isolated', 'Изолированная'), ('cross', 'Кросс-маржа')],
        default='isolated'
    )
    currency = models.CharField(max_length=10, default='USD')
    leverage = models.IntegerField(default=1)
    deposit_percent = models.IntegerField(default=10)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Настройки {self.user.username}"
    

class News(models.Model):
    """Модель для хранения финансовых новостей"""
    title = models.CharField(max_length=500, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL-slug")
    summary = models.TextField(verbose_name="Краткое описание")
    content = models.TextField(verbose_name="Полный текст")
    source = models.CharField(max_length=100, verbose_name="Источник")
    source_url = models.URLField(blank=True, verbose_name="Ссылка на источник")
    image_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на изображение")
    category = models.CharField(max_length=50, default='Рынки', verbose_name="Категория")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Изображение")
    published_at = models.DateTimeField(verbose_name="Дата публикации")
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False, verbose_name="Важная новость")
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'slug': self.slug})