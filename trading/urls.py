from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('instruments/', views.instruments, name='instruments'),
    path('stock/<slug:slug>/', views.stock_detail, name='stock_detail'),
    path('buy/<int:stock_id>/', views.buy_stock, name='buy_stock'),
    path('deposit/', views.deposit, name='deposit'),
    path('about/', views.about_invest, name='about_invest'),
    path('news/', views.news, name='news'),
    path('news/', views.news_list, name='news'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('decision/', views.trading_decision, name='trading_decision'),
    path('configure/', views.configure_app, name='configure_app'),
    path('confirm/', views.confirm_settings, name='confirm_settings'),
    path('connect-api/', views.connect_api, name='connect_api'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/portfolio/edit/<int:portfolio_id>/', views.portfolio_edit, name='portfolio_edit'),
    path('profile/portfolio/delete/<int:portfolio_id>/', views.portfolio_delete, name='portfolio_delete'),
    
]