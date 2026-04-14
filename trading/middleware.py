# trading/middleware.py
from datetime import datetime
from django.core.cache import cache

class NewsUpdateMiddleware:
    """Middleware для проверки наличия новостей"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем, есть ли новости в базе
        last_check = cache.get('news_check')
        
        if not last_check:
            from .models import News
            from .news_fetcher import create_sample_news
            
            if News.objects.count() == 0:
                create_sample_news()
            
            cache.set('news_check', datetime.now(), 3600)
        
        response = self.get_response(request)
        return response