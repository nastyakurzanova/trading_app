from django.core.management.base import BaseCommand
from trading.news_fetcher import fetch_and_save_news, create_sample_news
from trading.models import News

class Command(BaseCommand):
    help = 'Обновляет новости из RSS-лент'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка новостей...')
        
        try:
            if News.objects.count() == 0:
                count = create_sample_news()
                self.stdout.write(f'Создано {count} демо-новостей')
            else:
                count = fetch_and_save_news()
                self.stdout.write(self.style.SUCCESS(f'Успешно добавлено {count} новых новостей'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))