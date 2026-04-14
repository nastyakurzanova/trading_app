# trading/views.py
import csv
from .models import StockPortfolio, StockItem, UserAPIKey, TradingSettings, UserPay, Category
from django.db.models import Sum
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
import matplotlib
matplotlib.use('Agg')  # обязательно до импорта pyplot
import matplotlib.pyplot as plt
import io
import urllib.parse
import base64
from django.http import JsonResponse
from .forms import TradingSettingsForm, APIKeyForm, RegisterForm
from .models import StockPortfolio, StockItem, UserAPIKey, TradingSettings
from .data_fetcher import fetch_historical_data
from .ai_model import predict_future_price, calculate_confidence

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


def home(request):
    return render(request, 'trading/dashboard.html')


@login_required
def dashboard(request):
    """Блок 1: Запустить приложение (пользователь уже авторизован и видит дашборд)"""
    portfolio = StockPortfolio.objects.filter(user=request.user, deleted_at__isnull=True)
    total_value = sum(item.price * item.quantity for item in portfolio)
    settings = TradingSettings.objects.filter(user=request.user).first()
    trading_active = settings.is_active if settings else False

    context = {
        'portfolio': portfolio,
        'total_value': total_value,
        'trading_active': trading_active,
    }
    return render(request, 'trading/dashboard.html', context)

@login_required
def refresh_news(request):
    """Ручное обновление новостей"""
    if request.method == 'POST':
        from .news_fetcher import create_sample_news
        from .models import News
        
        # Удаляем старые новости
        News.objects.all().delete()
        
        # Создаём новые
        count = create_sample_news()
        messages.success(request, f'Загружено {count} свежих новостей')
    return redirect('news')

import csv
from django.http import HttpResponse
import json

@login_required
def analytics(request):
    # Получаем параметры из запроса
    symbol = request.GET.get('symbol', 'EUR/USD')
    period = request.GET.get('period', '1M')
    refresh = request.GET.get('refresh', False)
    
    # Определяем количество дней для загрузки
    period_days = {
        '1D': 1,
        '1W': 7,
        '1M': 30,
        '3M': 90,
        '6M': 180,
        '1Y': 365,
    }
    days = period_days.get(period, 30)
    
    # Загружаем данные
    data = fetch_historical_data(symbol, count=max(days, 2))  # Минимум 2 точки для графика
    
    chart_uri = None
    prediction = None
    confidence = 65
    direction = 'рост'
    
    if data is not None and not data.empty:
        # Создаём график
        plt.figure(figsize=(12, 6))
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Проверяем количество точек данных
        if len(data) <= 2:
            # Для малого количества данных показываем точки и линию
            plt.plot(data.index, data['close'], label='Цена закрытия', color='#1a5f7a', 
                    linewidth=2, marker='o', markersize=8, markerfacecolor='#0d9488', markeredgecolor='white')
            
            # Добавляем горизонтальную линию текущей цены
            current_price = data['close'].iloc[-1]
            plt.axhline(y=current_price, color='#1a5f7a', linestyle='--', alpha=0.3, 
                       label=f'Текущая: {current_price:.4f}')
            
            # Добавляем аннотацию с ценой
            plt.annotate(f'{current_price:.4f}', 
                        xy=(data.index[-1], current_price),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=10, fontweight='bold', color='#1a5f7a')
            
            plt.title(f'{symbol} - Текущая цена: {current_price:.4f}', 
                     fontsize=16, fontweight='bold', pad=20)
        else:
            # Основной график цены закрытия
            plt.plot(data.index, data['close'], label='Цена закрытия', 
                    color='#1a5f7a', linewidth=2)
            
            # Добавляем скользящие средние только если данных достаточно
            if len(data) >= 5:
                ma5 = data['close'].rolling(window=5).mean()
                plt.plot(data.index, ma5, label='MA 5', color='#0d9488', 
                        linewidth=1, alpha=0.7, linestyle='--')
            
            if len(data) >= 10:
                ma10 = data['close'].rolling(window=10).mean()
                plt.plot(data.index, ma10, label='MA 10', color='#d00000', 
                        linewidth=1, alpha=0.7, linestyle='--')
            
            if len(data) >= 20:
                ma20 = data['close'].rolling(window=20).mean()
                plt.plot(data.index, ma20, label='MA 20', color='#e85d04', 
                        linewidth=1.5, alpha=0.8)
            
            if len(data) >= 50:
                ma50 = data['close'].rolling(window=50).mean()
                plt.plot(data.index, ma50, label='MA 50', color='#6a4c93', 
                        linewidth=1, alpha=0.6)
            
            # Определяем изменение за период
            price_change = data['close'].iloc[-1] - data['close'].iloc[0]
            change_percent = (price_change / data['close'].iloc[0]) * 100
            change_color = '#2b9348' if price_change >= 0 else '#d00000'
            change_symbol = '▲' if price_change >= 0 else '▼'
            
            plt.title(f'Динамика {symbol} | {change_symbol} {change_percent:+.2f}% за период', 
                     fontsize=16, fontweight='bold', pad=20, color=change_color)
        
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Цена', fontsize=12)
        plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
        plt.grid(True, alpha=0.3)
        
        # Форматируем ось X
        if len(data) > 1:
            plt.gcf().autofmt_xdate()
        
        # Добавляем заливку под графиком для красоты
        if len(data) > 2:
            plt.fill_between(data.index, data['close'], alpha=0.1, color='#1a5f7a')
        
        plt.tight_layout()
        
        # Сохраняем в base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        chart_uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        plt.close()
        
        # Получаем прогноз
        prediction = predict_future_price(data)
        confidence, direction = calculate_confidence(data)
    
    # Получаем список доступных символов
    from .data_fetcher import get_available_symbols
    symbols = get_available_symbols()
    
    # Если это AJAX запрос на обновление прогноза
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'prediction': prediction,
            'confidence': confidence,
            'direction': direction,
        })
    
    # Если запрос на скачивание отчёта
    if request.GET.get('download') == 'report':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="analytics_report_{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response.write(u'\ufeff'.encode('utf8'))  # BOM для Excel
        
        writer = csv.writer(response)
        writer.writerow(['Аналитический отчёт TradeAI'])
        writer.writerow(['Сгенерирован:', datetime.now().strftime("%d.%m.%Y %H:%M:%S")])
        writer.writerow(['Инструмент:', symbol])
        writer.writerow(['Период:', period])
        writer.writerow([])
        
        if data is not None and not data.empty:
            writer.writerow(['Статистика за период'])
            writer.writerow(['Период:', f"{data.index[0].strftime('%d.%m.%Y %H:%M')} - {data.index[-1].strftime('%d.%m.%Y %H:%M')}"])
            writer.writerow(['Открытие периода:', round(data['close'].iloc[0], 4)])
            writer.writerow(['Закрытие периода:', round(data['close'].iloc[-1], 4)])
            
            if 'high' in data.columns:
                writer.writerow(['Максимум:', round(data['high'].max(), 4)])
                writer.writerow(['Минимум:', round(data['low'].min(), 4)])
            else:
                writer.writerow(['Максимум:', round(data['close'].max(), 4)])
                writer.writerow(['Минимум:', round(data['close'].min(), 4)])
            
            change = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0] * 100
            writer.writerow(['Изменение:', f"{round(change, 2)}%"])
            writer.writerow([])
            writer.writerow(['Прогноз на 24 часа'])
            writer.writerow(['Прогнозируемая цена:', prediction if prediction else 'Н/Д'])
            writer.writerow(['Вероятность:', f"{confidence}% ({direction})"])
            writer.writerow([])
            writer.writerow(['Исторические данные'])
            writer.writerow(['Дата', 'Открытие', 'Максимум', 'Минимум', 'Закрытие', 'Объём'])
            
            for idx in data.tail(50).index:
                row = data.loc[idx]
                writer.writerow([
                    idx.strftime('%d.%m.%Y %H:%M'),
                    round(row.get('open', row['close']), 4),
                    round(row.get('high', row['close']), 4),
                    round(row.get('low', row['close']), 4),
                    round(row['close'], 4),
                    int(row.get('volume', 0))
                ])
        
        return response
    
    context = {
        'chart_uri': chart_uri,
        'prediction': prediction,
        'confidence': confidence,
        'direction': direction,
        'symbols': symbols,
        'current_symbol': symbol,
        'current_period': period,
        'last_update': datetime.now().strftime("%H:%M:%S"),
    }
    return render(request, 'trading/analytics.html', context)



@login_required
def instruments(request):
    """Страница доступных инструментов с фильтрацией"""
    stocks = StockItem.objects.all()
    category_filter = request.GET.get('category', 'all')
    
    if category_filter != 'all':
        stocks = stocks.filter(category__title=category_filter)
    
    # Получаем все категории для фильтра
    from .models import Category
    categories = Category.objects.all()
    
    context = {
        'stocks': stocks,
        'categories': categories,
        'current_category': category_filter,
    }
    return render(request, 'trading/instruments.html', context)

@login_required
def stock_detail(request, slug):
    """Детальная страница актива"""
    stock = get_object_or_404(StockItem, slug=slug)
    
    # Получаем исторические данные для графика
    data = fetch_historical_data(stock.title, count=30)
    
    chart_uri = None
    if data is not None and not data.empty:
        plt.figure(figsize=(10, 4))
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.plot(data.index, data['close'], color='#1a5f7a', linewidth=2)
        plt.fill_between(data.index, data['close'], alpha=0.1, color='#1a5f7a')
        plt.title(f'{stock.title} - 30 дней', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        chart_uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        plt.close()
    
    # Проверяем, есть ли актив в портфеле пользователя
    in_portfolio = StockPortfolio.objects.filter(
        user=request.user, 
        stock=stock, 
        deleted_at__isnull=True
    ).exists()
    
    context = {
        'stock': stock,
        'chart_uri': chart_uri,
        'in_portfolio': in_portfolio,
    }
    return render(request, 'trading/stock_detail.html', context)


@login_required
def buy_stock(request, stock_id):
    """Покупка актива"""
    if request.method == 'POST':
        stock = get_object_or_404(StockItem, id=stock_id)
        quantity = int(request.POST.get('quantity', 1))
        currency = request.POST.get('currency', stock.currency)
        price = float(request.POST.get('price', stock.close_price))
        
        # Создаём или обновляем позицию в портфеле
        portfolio_item, created = StockPortfolio.objects.get_or_create(
            user=request.user,
            stock=stock,
            deleted_at__isnull=True,
            defaults={
                'currency': currency,
                'price': price,
                'quantity': quantity
            }
        )
        
        if not created:
            # Если уже есть, увеличиваем количество
            portfolio_item.quantity += quantity
            portfolio_item.save()
        
        messages.success(request, f"Куплено {quantity} {stock.title} на сумму {price * quantity:.2f} {currency}")
        
    return redirect('instruments')


@login_required
def deposit(request):
    """Страница пополнения счёта"""
    from .models import UserPay
    from django.db.models import Sum
    from django.contrib import messages
    
    # Текущий баланс (сумма всех активов в портфеле)
    portfolio = StockPortfolio.objects.filter(user=request.user, deleted_at__isnull=True)
    current_balance = sum(item.price * item.quantity for item in portfolio)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_type = request.POST.get('payment_type')
        acquiring = request.POST.get('acquiring')
        
        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Сумма должна быть больше нуля")
            else:
                # Создаём запись о платеже
                UserPay.objects.create(
                    user=request.user,
                    amount=amount,
                    payment_type=payment_type,
                    acquiring=acquiring
                )
                messages.success(request, f"Счёт успешно пополнен на ${amount:.2f}")
                return redirect('dashboard')
        except ValueError:
            messages.error(request, "Введите корректную сумму")
    
    # Получаем историю платежей пользователя
    payments = UserPay.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    # Считаем общую сумму пополнений
    total_deposits = UserPay.objects.filter(user=request.user).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'payments': payments,
        'total_deposits': total_deposits,
        'current_balance': current_balance,
    }
    return render(request, 'trading/deposit.html', context)

def about_invest(request):
    return render(request, 'trading/about_invest.html')


def news(request):
    """Страница со списком новостей"""
    from .models import News
    
    # Получаем все новости
    all_news = News.objects.all().order_by('-published_at')
    
    category = request.GET.get('category', 'all')
    
    if category != 'all':
        all_news = all_news.filter(category=category)
    
    # Получаем уникальные категории
    categories = News.objects.values_list('category', flat=True).distinct().order_by('category')
    
    # Важные новости
    featured_news = all_news.filter(is_featured=True)[:3]
    
    # Обычные новости
    regular_news = all_news.exclude(id__in=featured_news.values_list('id', flat=True))
    
    context = {
        'featured_news': featured_news,
        'news': regular_news,
        'categories': categories,
        'current_category': category,
    }
    return render(request, 'trading/news.html', context)

from django.core.cache import cache
from datetime import datetime, timedelta

def news_list(request):
    """Страница со списком новостей"""
    from .models import News
    
    # Получаем все новости
    all_news = News.objects.all().order_by('-published_at')
    
    category = request.GET.get('category', 'all')
    
    if category != 'all':
        all_news = all_news.filter(category=category)
    
    # Получаем уникальные категории
    categories = News.objects.values_list('category', flat=True).distinct().order_by('category')
    
    # Важные новости
    featured_news = all_news.filter(is_featured=True)[:3]
    
    # Обычные новости
    regular_news = all_news.exclude(id__in=featured_news.values_list('id', flat=True))
    
    # Отладка в консоли
    print(f"Всего новостей: {all_news.count()}")
    print(f"Важных: {featured_news.count()}")
    print(f"Обычных: {regular_news.count()}")
    
    context = {
        'featured_news': featured_news,
        'news': regular_news,
        'categories': categories,
        'current_category': category,
    }
    return render(request, 'trading/news.html', context)


def news_detail(request, slug):
    """Детальная страница новости"""
    from .models import News
    news = get_object_or_404(News, slug=slug)
    
    # Похожие новости
    related_news = News.objects.filter(
        category=news.category
    ).exclude(id=news.id)[:3]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'trading/news_detail.html', context)

def news_detail(request, slug):
    """Детальная страница новости"""
    from .models import News
    news = get_object_or_404(News, slug=slug)
    
    # Получаем похожие новости
    related_news = News.objects.filter(
        category=news.category
    ).exclude(id=news.id)[:3]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'trading/news_detail.html', context)

# ---------- БЛОК 2: Подключение к рынку (API ключи) ----------
@login_required
def connect_api(request):
    """Пользователь вводит свои API ключи для подключения к аккаунту на торговой платформе"""
    api_key_obj = UserAPIKey.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = APIKeyForm(request.POST, instance=api_key_obj)
        if form.is_valid():
            new_key = form.save(commit=False)
            new_key.user = request.user
            new_key.is_active = True
            new_key.save()
            messages.success(request, "API ключи успешно сохранены. Подключение к рынку выполнено.")
            return redirect('dashboard')
    else:
        form = APIKeyForm(instance=api_key_obj)
    return render(request, 'trading/connect_api.html', {'form': form})


# ---------- БЛОК 3: Настройка приложения (31-35) ----------
@login_required
def configure_app(request):
    """Пользователь выбирает параметры торговли (31-34)"""
    settings_obj, created = TradingSettings.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = TradingSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            return redirect('confirm_settings')
    else:
        form = TradingSettingsForm(instance=settings_obj)
    return render(request, 'trading/configure_app.html', {'form': form})


@login_required
def confirm_settings(request):
    """Пользователь проверяет и подтверждает введенные параметры (35)"""
    settings_obj = get_object_or_404(TradingSettings, user=request.user)
    if request.method == 'POST':
        settings_obj.is_active = True
        settings_obj.save()
        messages.success(request, "Настройки подтверждены. Торговля активирована!")
        # Блок 4 (уведомление) – здесь можно отправить реальное уведомление (пока через messages)
        return redirect('dashboard')
    context = {'settings': settings_obj}
    return render(request, 'trading/confirm_settings.html', context)


@login_required
def trading_decision(request):
    # Создаём или получаем настройки
    settings, created = TradingSettings.objects.get_or_create(
        user=request.user,
        defaults={
            'margin_type': 'isolated',
            'currency': 'USD',
            'leverage': 1,
            'deposit_percent': 10,
            'is_active': False
        }
    )
    
    portfolio = StockPortfolio.objects.filter(user=request.user, deleted_at__isnull=True)
    total_value = sum(item.price * item.quantity for item in portfolio)

    report_lines = [
        f"Общая стоимость портфеля: ${total_value:.2f}",
        f"Активных позиций: {portfolio.count()}",
        f"Используемое плечо: 1:{settings.leverage}",
        f"Торгуемый процент депозита: {settings.deposit_percent}%",
    ]

    data = fetch_historical_data('EUR/USD', count=20)
    prediction = predict_future_price(data) if data is not None else None
    if prediction:
        report_lines.append(f"Прогноз цены EUR/USD: {prediction:.4f}")

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'stop':
            settings.is_active = False
            settings.save()
            messages.info(request, "Торговля остановлена по вашему решению.")
            return redirect('dashboard')
        elif action == 'continue':
            settings.is_active = True
            settings.save()
            messages.success(request, "Торговля продолжается. Удачных сделок!")
            return redirect('dashboard')

    context = {
        'report_lines': report_lines,
        'trading_active': settings.is_active,
    }
    return render(request, 'trading/trading_decision.html', context)