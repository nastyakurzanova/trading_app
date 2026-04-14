from django.contrib import admin
from django.urls import path, include
from trading.views import RegisterView  # теперь должен работать

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('trading.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', RegisterView.as_view(), name='register'),
]