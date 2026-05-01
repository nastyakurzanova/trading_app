from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from trading.views import RegisterView, CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('trading.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]