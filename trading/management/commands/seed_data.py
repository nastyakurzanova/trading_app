from django.core.management.base import BaseCommand
from trading.models import Category, StockItem, News
from django.utils.text import slugify
from datetime import datetime


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми торговыми инструментами и новостями'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        # Создаём категории
        forex, _ = Category.objects.get_or_create(
            title='Форекс', 
            defaults={'slug': 'forex'}
        )
        crypto, _ = Category.objects.get_or_create(
            title='Крипто', 
            defaults={'slug': 'crypto'}
        )
        stocks, _ = Category.objects.get_or_create(
            title='Акции', 
            defaults={'slug': 'stocks'}
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Категории созданы'))
        
        # Создаём торговые инструменты
        instruments = [
            # Форекс
            {'title': 'EUR/USD', 'full_name': 'Евро / Доллар США', 'category': forex, 'currency': 'USD', 'open_price': 1.0850, 'close_price': 1.0875, 'sector': 'Валютные пары'},
            {'title': 'GBP/USD', 'full_name': 'Фунт / Доллар США', 'category': forex, 'currency': 'USD', 'open_price': 1.2630, 'close_price': 1.2610, 'sector': 'Валютные пары'},
            {'title': 'USD/JPY', 'full_name': 'Доллар / Йена', 'category': forex, 'currency': 'JPY', 'open_price': 148.50, 'close_price': 149.10, 'sector': 'Валютные пары'},
            {'title': 'USD/RUB', 'full_name': 'Доллар / Рубль', 'category': forex, 'currency': 'RUB', 'open_price': 92.50, 'close_price': 93.20, 'sector': 'Валютные пары'},
            {'title': 'EUR/RUB', 'full_name': 'Евро / Рубль', 'category': forex, 'currency': 'RUB', 'open_price': 100.35, 'close_price': 101.50, 'sector': 'Валютные пары'},
            {'title': 'CNY/RUB', 'full_name': 'Юань / Рубль', 'category': forex, 'currency': 'RUB', 'open_price': 12.80, 'close_price': 12.95, 'sector': 'Валютные пары'},
            
            # Криптовалюты
            {'title': 'BTC/USD', 'full_name': 'Биткоин', 'category': crypto, 'currency': 'USD', 'open_price': 65200.00, 'close_price': 65850.00, 'sector': 'Криптовалюты'},
            {'title': 'ETH/USD', 'full_name': 'Ethereum', 'category': crypto, 'currency': 'USD', 'open_price': 3480.00, 'close_price': 3520.00, 'sector': 'Криптовалюты'},
            {'title': 'USDT/RUB', 'full_name': 'Tether / Рубль', 'category': crypto, 'currency': 'RUB', 'open_price': 92.50, 'close_price': 93.00, 'sector': 'Стейблкоины'},
            
            # Российские акции
            {'title': 'SBER', 'full_name': 'Сбербанк', 'category': stocks, 'currency': 'RUB', 'open_price': 285.50, 'close_price': 287.30, 'sector': 'Финансы'},
            {'title': 'GAZP', 'full_name': 'Газпром', 'category': stocks, 'currency': 'RUB', 'open_price': 168.20, 'close_price': 169.50, 'sector': 'Нефтегаз'},
            {'title': 'LKOH', 'full_name': 'Лукойл', 'category': stocks, 'currency': 'RUB', 'open_price': 7450.00, 'close_price': 7480.00, 'sector': 'Нефтегаз'},
            {'title': 'ROSN', 'full_name': 'Роснефть', 'category': stocks, 'currency': 'RUB', 'open_price': 580.30, 'close_price': 582.10, 'sector': 'Нефтегаз'},
            {'title': 'NVTK', 'full_name': 'Новатэк', 'category': stocks, 'currency': 'RUB', 'open_price': 1420.00, 'close_price': 1435.00, 'sector': 'Нефтегаз'},
            {'title': 'TATN', 'full_name': 'Татнефть', 'category': stocks, 'currency': 'RUB', 'open_price': 720.50, 'close_price': 722.00, 'sector': 'Нефтегаз'},
            {'title': 'GMKN', 'full_name': 'Норникель', 'category': stocks, 'currency': 'RUB', 'open_price': 16800.00, 'close_price': 16850.00, 'sector': 'Металлургия'},
            {'title': 'AFLT', 'full_name': 'Аэрофлот', 'category': stocks, 'currency': 'RUB', 'open_price': 52.30, 'close_price': 52.80, 'sector': 'Транспорт'},
            {'title': 'MTSS', 'full_name': 'МТС', 'category': stocks, 'currency': 'RUB', 'open_price': 310.40, 'close_price': 311.20, 'sector': 'Телеком'},
            {'title': 'MOEX', 'full_name': 'Московская Биржа', 'category': stocks, 'currency': 'RUB', 'open_price': 235.60, 'close_price': 236.10, 'sector': 'Финансы'},
            {'title': 'PLZL', 'full_name': 'Полюс', 'category': stocks, 'currency': 'RUB', 'open_price': 14500.00, 'close_price': 14600.00, 'sector': 'Золотодобыча'},
            
            # Американские акции
            {'title': 'AAPL', 'full_name': 'Apple Inc.', 'category': stocks, 'currency': 'USD', 'open_price': 175.50, 'close_price': 177.20, 'sector': 'Технологии'},
            {'title': 'TSLA', 'full_name': 'Tesla Inc.', 'category': stocks, 'currency': 'USD', 'open_price': 248.30, 'close_price': 245.80, 'sector': 'Автопром'},
            {'title': 'NVDA', 'full_name': 'NVIDIA Corporation', 'category': stocks, 'currency': 'USD', 'open_price': 850.20, 'close_price': 860.50, 'sector': 'Технологии'},
        ]
        
        count = 0
        for inst in instruments:
            slug = slugify(inst['title'][:40])
            _, created = StockItem.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': inst['title'],
                    'full_name': inst.get('full_name', ''),
                    'category': inst['category'],
                    'currency': inst['currency'],
                    'open_price': inst['open_price'],
                    'close_price': inst['close_price'],
                    'sector': inst.get('sector', ''),
                    'description': f"{inst.get('full_name', inst['title'])} — торговый инструмент на финансовом рынке.",
                }
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {count} новых инструментов (всего: {StockItem.objects.count()})'))
        
        # Создаём новости, если их нет
        if News.objects.count() == 0:
            from trading.news_fetcher import create_sample_news
            news_count = create_sample_news()
            self.stdout.write(self.style.SUCCESS(f'✓ Создано {news_count} новостей'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ База данных успешно заполнена!'))
        self.stdout.write(f'   Категорий: {Category.objects.count()}')
        self.stdout.write(f'   Инструментов: {StockItem.objects.count()}')
        self.stdout.write(f'   Новостей: {News.objects.count()}')