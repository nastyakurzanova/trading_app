# trading/ai_model.py
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def predict_future_price(data, days_ahead=1):
    """
    Прогнозирует цену на основе взвешенного среднего и тренда.
    """
    if data is None or data.empty:
        return None
    
    try:
        # Получаем цены закрытия
        if 'close' in data.columns:
            prices = data['close'].values
        elif 'Close' in data.columns:
            prices = data['Close'].values
        else:
            return None
            
        if len(prices) < 5:
            return round(float(prices[-1]), 4)
            
        # Взвешенное среднее (последние значения важнее)
        n = min(20, len(prices))
        weights = np.exp(np.linspace(-1, 0, n))
        weights = weights / weights.sum()
        
        last_n = prices[-n:]
        weighted_avg = np.sum(last_n * weights)
        
        # Расчёт тренда
        if len(prices) >= 10:
            short_trend = prices[-1] - prices[-5]
            long_trend = prices[-1] - prices[-min(10, len(prices))]
            trend = (short_trend * 0.7 + long_trend * 0.3) / 5
        else:
            trend = 0
            
        prediction = weighted_avg + trend * days_ahead
        
        return round(float(prediction), 4)
        
    except Exception as e:
        print(f"Ошибка прогноза: {e}")
        if 'prices' in locals() and len(prices) > 0:
            return round(float(prices[-1]), 4)
        return None


def calculate_confidence(data):
    """
    Рассчитывает уверенность прогноза и направление.
    ВСЕГДА возвращает кортеж (confidence, direction)
    """
    # Значения по умолчанию
    default_confidence = 65
    default_direction = 'рост'
    
    if data is None or data.empty:
        return default_confidence, default_direction
    
    try:
        # Получаем цены
        if 'close' in data.columns:
            prices = data['close'].values
        elif 'Close' in data.columns:
            prices = data['Close'].values
        else:
            return default_confidence, default_direction
            
        if len(prices) < 5:
            return default_confidence, default_direction
            
        # Расчёт волатильности
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * 100  # В процентах
        
        # Базовая уверенность (чем ниже волатильность, тем выше уверенность)
        confidence = max(55, min(95, 90 - volatility * 100))
        
        # Определение направления
        if len(prices) >= 10:
            ma_short = np.mean(prices[-5:])
            ma_long = np.mean(prices[-10:])
            
            if ma_short > ma_long:
                direction = 'рост'
                confidence = min(95, confidence * 1.1)
            else:
                direction = 'падение'
                confidence = confidence * 0.9
        else:
            # Если мало данных, смотрим на последнее изменение
            if prices[-1] > prices[0]:
                direction = 'рост'
            else:
                direction = 'падение'
        
        # Округляем и возвращаем
        return int(round(confidence)), direction
        
    except Exception as e:
        print(f"Ошибка расчёта уверенности: {e}")
        return default_confidence, default_direction


def load_keras_model():
    """Заглушка для совместимости"""
    return None