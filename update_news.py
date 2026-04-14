import os
import sys
import django

# Укажите путь к вашему проекту
sys.path.append(r'C:\Users\nastya\МГТУ\trading_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from trading.news_fetcher import fetch_and_save_news

if __name__ == '__main__':
    print("Загрузка новостей...")
    count = fetch_and_save_news()
    print(f"Добавлено {count} новых новостей.")