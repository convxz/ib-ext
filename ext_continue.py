import pandas as pd


def ext_continue(data: pd.DataFrame, ep: float, sl: float, rr:int=1):
        """
        Проверяет, достиг ли рынок тейк-профита или стоп-лосса после входа в сделку.
        Возвращает:
        - (True, time) — если сначала был достигнут тейк
        - (False, time) — если сначала был достигнут стоп
        """
        delta = abs(ep-sl)
        is_long = ep > sl

        for idx, row in data.iterrows():
            if is_long:
                tp = ep + delta * rr
                if row["low"] <= sl:
                    return False, idx
                if row["high"] >= tp:
                    return True, idx
            else:
                tp = ep - delta * rr
                if row["high"] >= sl:
                    return False, idx
                if row["low"] <= tp:
                    return True, idx
        return False, None  # Если ничего из этого не было
