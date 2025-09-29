import pandas as pd
from is_fractal import is_fractal

def check_test_ib(first_ext_direction: bool, min_ib: float, max_ib: float, day_dft: pd.DataFrame):
    """
    Определяет момент первого теста зоны IB после выхода с формированием фрактала.
    Тест IB валиден только если между выходом и тестом был хотя бы один фрактал.
    
    args:
        first_ext_direction (bool): True – пробой вверх, False – пробой вниз
        min_ib (float): нижняя граница IB
        max_ib (float): верхняя граница IB
        day_dft (pd.DataFrame): свечи с колонками 'high' и 'low' и индексом по времени

    return:
        tuple[float, pd.Timestamp] | None: (уровень фрактала, время центральной свечи фрактала) или None
    """
    out_of_ib = False
    extreme_level = None
    extreme_time = None

    for idx in range(len(day_dft)):
        candle = day_dft.iloc[idx]

        # --- фиксация выхода из IB ---
        if not out_of_ib:
            if first_ext_direction and candle.high > max_ib:
                out_of_ib = True
            elif not first_ext_direction and candle.low < min_ib:
                out_of_ib = True
            continue

        # --- поиск фракталов после выхода ---
        if idx >= 2:  # нужно минимум 3 свечи
            last_3 = day_dft.iloc[idx-2:idx+1]  # центральная = текущая
            is_up, is_down, low_c, high_c = is_fractal(last_3)

            if first_ext_direction and is_up:
                # обновляем экстремум для пробоя вверх
                if extreme_level is None or high_c > extreme_level:
                    extreme_level = high_c
                    extreme_time = last_3.index[1]  # центральная свеча
            elif not first_ext_direction and is_down:
                # обновляем экстремум для пробоя вниз
                if extreme_level is None or low_c < extreme_level:
                    extreme_level = low_c
                    extreme_time = last_3.index[1]

        # --- проверка теста IB (валидный только если был фрактал) ---
        if first_ext_direction and candle.low <= max_ib:
            if extreme_level is not None:
                return extreme_level, extreme_time
        elif not first_ext_direction and candle.high >= min_ib:
            if extreme_level is not None:
                return extreme_level, extreme_time

    # если теста IB не было до конца дня или фрактала не было
    return None, None
