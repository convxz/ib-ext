def first_ext(min_ib, max_ib, day_dft):
    """
    Определяет первое направление выхода цены за границы initial balance (IB).

    args:
        min_ib (int | float): нижняя граница IB
        max_ib (int | float): верхняя граница IB
        day_dft (pd.DataFrame): таблица с колонками 'high' и 'low'
                                и индексом по времени (candles intraday)

    Логика работы:
        - Если какое-либо значение 'high' превысит max_ib раньше,
          чем 'low' уйдёт ниже min_ib → результат True (пробой вверх).
        - Если наоборот 'low' первым станет меньше min_ib →
          результат False (пробой вниз).
        - Если пробоев не было вообще → результат None.

    return:
        bool | None:
            True  – первый экстремум был выше max_ib
            False – первый экстремум был ниже min_ib
            None  – пробоя не зафиксировано
    """
    # Индексы строк, где произошёл выход
    cond_up = day_dft["high"] > max_ib
    cond_down = day_dft["low"] < min_ib

    # Находим первую позицию, где условие сработало
    first_up_idx = cond_up.idxmax() if cond_up.any() else None
    first_down_idx = cond_down.idxmax() if cond_down.any() else None

    # Сравниваем, какое событие случилось раньше
    if first_up_idx is not None and first_down_idx is not None:
        return True if first_up_idx < first_down_idx else False
    elif first_up_idx is not None:
        return True
    elif first_down_idx is not None:
        return False
    else:
        return None
    