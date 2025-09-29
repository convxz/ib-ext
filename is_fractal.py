import pandas as pd

def is_fractal(df: pd.DataFrame):
    """
    Определяет наличие фрактала (вверх или вниз) на центральной свече 
    из последних трёх баров.

    args:
        df (pd.DataFrame): таблица с колонками 'high' и 'low'
                           и индексом по времени (candles intraday)

    Логика работы:
        - Берутся последние три свечи.
        - Проверяется, выше ли центральный high соседних → фрактал вверх.
        - Проверяется, ниже ли центральный low соседних → фрактал вниз.
        - Если ни одно условие не выполнено → фрактала нет.

    return:
        tuple[bool, bool, float, float]:
            (is_fractal_up, is_fractal_down, low_center, high_center)
                is_fractal_up (bool)   – True, если зафиксирован фрактал вверх
                is_fractal_down (bool) – True, если зафиксирован фрактал вниз
                low_center (float)     – low центральной свечи
                high_center (float)    – high центральной свечи

            None – если в df меньше трёх свечей
    """
    if df is None:
        return None
    if len(df) < 3:
        return None
        
    # Берем последние три бара
    last_3 = df.tail(3)

    # Извлекаем значения high и low
    high_left, high_center, high_right = last_3['high'].values
    low_left,  low_center,  low_right  = last_3['low'].values

    # Условия фракталов
    is_fractal_up = high_center > high_left and high_center > high_right
    is_fractal_down = low_center < low_left and low_center < low_right

    return is_fractal_up, is_fractal_down, low_center, high_center
