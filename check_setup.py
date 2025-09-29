import pandas as pd
from is_fractal import is_fractal

def check_setup(min_ib, max_ib, first_ext_direction, bos_level, bos_dt, day_dft: pd.DataFrame):
    """
    Возвращает кортеж (результат, время):
        результат: True — экст подтверждён, False — рейд, None — если ни одно условие не выполнено до конца дня
        время: метка свечи, на которой условие выполнено (или None, если до конца дня не было сигнала)
    """
    df = day_dft.loc[bos_dt:]
    bos_current = bos_level

    for i in range(len(df)):
        window = df.iloc[:i+1]  # все свечи до текущей включительно
        candle = df.iloc[i]

        # проверка фрактала на окне
        fractal = is_fractal(window)
        if fractal:
            is_up, is_down, low_center, high_center = fractal

            if first_ext_direction:  # вверх
                if is_up and high_center > bos_current:
                    bos_current = high_center
            else:  # вниз
                if is_down and low_center < bos_current:
                    bos_current = low_center

        # проверка условий закрытия
        if first_ext_direction:  # вверх
            if candle['close'] > bos_current:
                return True, candle.name  # candle.name = индекс (время)
            if candle['close'] < min_ib:
                return False, candle.name
        else:  # вниз
            if candle['close'] < bos_current:
                return True, candle.name
            if candle['close'] > max_ib:
                return False, candle.name

    return None, None
