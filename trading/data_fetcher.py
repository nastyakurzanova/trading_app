# trading/data_fetcher.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def fetch_historical_data(symbol='EUR/USD', count=100):
    """
    Генерирует реалистичные синтетические данные для демонстрации.
    """
    dates = pd.date_range(end=datetime.now(), periods=count, freq='D')
    
    # Базовые цены для разных символов (в рублях для российских активов)
    base_prices = {
        # Форекс
        'EUR/USD': 1.0850,
        'GBP/USD': 1.2630,
        'USD/JPY': 148.50,
        'USD/RUB': 92.50,
        'EUR/RUB': 100.35,
        'CNY/RUB': 12.80,
        # Криптовалюты
        'BTC/USD': 65200,
        'ETH/USD': 3480,
        'USDT/RUB': 92.50,
        # Акции США
        'AAPL': 175.50,
        'TSLA': 248.30,
        'NVDA': 850.20,
        # Российские акции (в рублях)
        'SBER': 285.50,
        'GAZP': 168.20,
        'LKOH': 7450.00,
        'ROSN': 580.30,
        'NVTK': 1420.00,
        'TATN': 720.50,
        'GMKN': 16800.00,
        'AFLT': 52.30,
        'MTSS': 310.40,
        'VTBR': 0.0235,
        'MOEX': 235.60,
        'PLZL': 14500.00,
    }
    
    base = base_prices.get(symbol, 100.0)
    
    # Генерируем реалистичное случайное блуждание
    returns = np.random.randn(count) * 0.01  # 1% волатильность
    prices = base * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        'open': prices * (1 + np.random.randn(count) * 0.001),
        'high': prices * (1 + np.abs(np.random.randn(count) * 0.005)),
        'low': prices * (1 - np.abs(np.random.randn(count) * 0.005)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, count)
    }, index=dates)
    
    return df


def get_available_symbols():
    """Возвращает список доступных символов для выбора"""
    return [
        # Форекс
        {'name': 'EUR/USD', 'symbol': 'EURUSD=X', 'category': 'Форекс', 'currency': 'USD'},
        {'name': 'GBP/USD', 'symbol': 'GBPUSD=X', 'category': 'Форекс', 'currency': 'USD'},
        {'name': 'USD/JPY', 'symbol': 'JPY=X', 'category': 'Форекс', 'currency': 'JPY'},
        {'name': 'USD/RUB', 'symbol': 'USDRUB=X', 'category': 'Форекс', 'currency': 'RUB'},
        {'name': 'EUR/RUB', 'symbol': 'EURRUB=X', 'category': 'Форекс', 'currency': 'RUB'},
        {'name': 'CNY/RUB', 'symbol': 'CNYRUB=X', 'category': 'Форекс', 'currency': 'RUB'},
        # Криптовалюты
        {'name': 'BTC/USD', 'symbol': 'BTC-USD', 'category': 'Крипто', 'currency': 'USD'},
        {'name': 'ETH/USD', 'symbol': 'ETH-USD', 'category': 'Крипто', 'currency': 'USD'},
        {'name': 'USDT/RUB', 'symbol': 'USDT-RUB', 'category': 'Крипто', 'currency': 'RUB'},
        # Акции США
        {'name': 'AAPL', 'symbol': 'AAPL', 'category': 'Акции', 'currency': 'USD'},
        {'name': 'TSLA', 'symbol': 'TSLA', 'category': 'Акции', 'currency': 'USD'},
        {'name': 'NVDA', 'symbol': 'NVDA', 'category': 'Акции', 'currency': 'USD'},
        # Российские акции
        {'name': 'SBER', 'symbol': 'SBER', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Сбербанк'},
        {'name': 'GAZP', 'symbol': 'GAZP', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Газпром'},
        {'name': 'LKOH', 'symbol': 'LKOH', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Лукойл'},
        {'name': 'ROSN', 'symbol': 'ROSN', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Роснефть'},
        {'name': 'NVTK', 'symbol': 'NVTK', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Новатэк'},
        {'name': 'TATN', 'symbol': 'TATN', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Татнефть'},
        {'name': 'GMKN', 'symbol': 'GMKN', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Норникель'},
        {'name': 'AFLT', 'symbol': 'AFLT', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Аэрофлот'},
        {'name': 'MTSS', 'symbol': 'MTSS', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'МТС'},
        {'name': 'VTBR', 'symbol': 'VTBR', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'ВТБ'},
        {'name': 'MOEX', 'symbol': 'MOEX', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'МосБиржа'},
        {'name': 'PLZL', 'symbol': 'PLZL', 'category': 'Акции', 'currency': 'RUB', 'full_name': 'Полюс'},
    ]