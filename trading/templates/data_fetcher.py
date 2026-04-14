import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

def fetch_historical_data(symbol='EURUSD=X', count=100):
    """
    Получает реальные исторические данные через Yahoo Finance.
    symbol: 'EURUSD=X' для EUR/USD, 'BTC-USD' для Bitcoin и т.д.
    """
    try:
        # Конвертируем символ в формат Yahoo Finance
        if symbol == 'EUR/USD':
            ticker = 'EURUSD=X'
        elif symbol == 'BTC/USD':
            ticker = 'BTC-USD'
        elif symbol == 'ETH/USD':
            ticker = 'ETH-USD'
        else:
            ticker = symbol
            
        # Получаем данные за последние N дней
        end_date = datetime.now()
        start_date = end_date - timedelta(days=count)
        
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError("Нет данных")
            
        # Переименовываем колонки для совместимости
        df = df.rename(columns={'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume'})
        return df
        
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}. Использую синтетические данные.")
        # Fallback на синтетические данные
        dates = pd.date_range(end=datetime.now(), periods=count, freq='D')
        base_price = 1.10 if 'EUR' in symbol else 100.0
        prices = base_price + np.cumsum(np.random.randn(count) * 0.01)
        return pd.DataFrame({'close': prices}, index=dates)

def get_available_symbols():
    """Возвращает список доступных символов"""
    return [
        {'name': 'EUR/USD', 'symbol': 'EURUSD=X', 'category': 'Форекс'},
        {'name': 'GBP/USD', 'symbol': 'GBPUSD=X', 'category': 'Форекс'},
        {'name': 'USD/JPY', 'symbol': 'JPY=X', 'category': 'Форекс'},
        {'name': 'BTC/USD', 'symbol': 'BTC-USD', 'category': 'Крипто'},
        {'name': 'ETH/USD', 'symbol': 'ETH-USD', 'category': 'Крипто'},
        {'name': 'AAPL', 'symbol': 'AAPL', 'category': 'Акции'},
        {'name': 'TSLA', 'symbol': 'TSLA', 'category': 'Акции'},
    ]