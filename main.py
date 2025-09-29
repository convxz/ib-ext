import pandas as pd
import json
from drawpos import drawpos, get_slice_pos
from is_fractal import is_fractal
from local_time import get_local_time_range
from ext_continue import ext_continue


def ext_setups(day_df: pd.DataFrame, full_df: pd.DataFrame, rr: int = 1) -> dict:
    log = {
        "min_ib": 0,
        "max_ib": 0,
        "first_ext": 0,
        "first_ext_time": 0,
        "bos_level": 0,
        "ib_test": 0,
        "setup": 0,
        "ep": 0,
        "sl": 0,
        "tp": 0,
        "ep_time": 0,
        "res": 0,
        "close_time": 0
    }

    # Определяем первое время дня
    date = day_df.index[0].to_pydatetime()
    # Проверим летнее ли время
    day_end = "14:57"
    ib_start, ib_end, day_start = get_local_time_range(date)

    ib_set = day_df.between_time(ib_start, ib_end)
    # границы иб
    min_ib, max_ib = ib_set["low"].min(), ib_set["high"].max()
    log["max_ib"], log["min_ib"] = max_ib, min_ib
    # сторона выхода в первую очередь
    first_ext = None
    # фрактал для боса (должен обновляться)
    bos_level = 0
    # был ли тестирован иб
    test_ib = False
    sl = 0
    ep = 0

    was_fractal = False

    day_dft = day_df.between_time(day_start, day_end)
    for dt, row in day_dft.iterrows():
        # print(dt, bos_level, row["open"], row["high"], row["low"], row["close"], row["volume"])
        if first_ext is None:
            if row["high"] > max_ib:
                first_ext = "up"
                log["first_ext"] = first_ext
                log["first_ext_time"] = dt
                bos_level = row["high"]
            elif row["low"] < min_ib:
                first_ext = "down"
                log["first_ext"] = first_ext
                log["first_ext_time"] = dt
                bos_level = row["low"]

        # up exit
        if first_ext == 'up':
            if not test_ib:
                bos_level = max(bos_level, row["high"])
                if row["low"] < max_ib:
                        test_ib = True
                        sl = min(row["low"], min_ib)
                        log["ib_test"] = dt
            else:
                sl = min(sl, row["low"])
                if not was_fractal:
                    dft = day_df.between_time(day_start, log["ib_test"].strftime("%H:%M"))
                    for dt, row in dft.iterrows():
                        is_fractal_now = is_fractal(dft[dft.index<=dt].tail(3))
                        if is_fractal_now is not None:
                            if is_fractal_now[0]:
                                bos_level = max(bos_level, is_fractal_now[3])
                                was_fractal = True

                else:
                    if row['close'] > min_ib:
                        is_fractal_now = is_fractal(day_dft[day_dft.index <= dt].tail(3))
                        if row["close"] > bos_level:
                            ep = row["close"]
                            log["setup"] = 'ext'
                            log["ep_time"] = dt
                            res, close_time = ext_continue(full_df[full_df.index >= dt], ep, sl)
                            log["tp"] = ep + (ep - sl) * rr if ep > sl else ep - (sl - ep) * rr
                            log["bos_level"] = bos_level
                            log["ep"] = ep
                            log["sl"] = sl
                            log["res"] = res
                            log['close_time'] = close_time
                            return log
                        if is_fractal_now is not None:
                            if is_fractal_now[0]:
                                bos_level = max(bos_level, float(is_fractal_now[3]))
                        
                    else: 
                        log['setup'] = 'raid'
                        ep = row["close"]
                        sl = bos_level
                        log["ep"] = ep
                        log["sl"] = sl
                        log["ep_time"] = dt
                        res, close_time = ext_continue(full_df[full_df.index >= dt], ep, sl)
                        log["tp"] = ep + (ep - sl) * rr if ep > sl else ep - (sl - ep) * rr
                        log['res'] = res
                        log['close_time'] = close_time
                        return log

        # down exit
        elif first_ext == 'down':
            if not test_ib:
                bos_level = min(bos_level, row["low"])
                if row["high"] > min_ib:
                    test_ib = True
                    sl = max(row["high"], max_ib)

                # is_fractal_now = is_fractal(day_dft[day_dft.index <= dt].tail(3))
                # if is_fractal_now is not None:
                #     if is_fractal_now[1]:
                #         was_fractal = True
                #         bos_level = min(bos_level, float(is_fractal_now[2]))
                # bos_level = min(bos_level, row["low"])
                # if row["low"] > min_ib:
                #     if was_fractal:
                #         test_ib = True
                #     sl = max(row["high"], max_ib)
            else:
                log["ib_test"] = dt
                # блок 
                sl = max(sl, row["high"])
                if not was_fractal:
                    dft = day_df.between_time(day_start, dt.strftime("%H:%M"))
                    for dt, row in dft.iterrows():
                        is_fractal_now = is_fractal(dft[dft.index <= dt].tail(3))
                        if is_fractal_now is not None:
                            if is_fractal_now[1]:
                                bos_level = max(bos_level, is_fractal_now[2])
                                was_fractal = True
                    if not was_fractal:
                        test_ib = False
                else:

                    if row['close'] < max_ib:
                        if row["close"] < bos_level:
                            # entry short
                            ep = row["close"]
                            log["setup"] = 'ext'
                            log["ep_time"] = dt
                            res, close_time = ext_continue(full_df[full_df.index >= dt], ep, sl)
                            log["tp"] = ep + (ep - sl) * rr if ep > sl else ep - (sl - ep) * rr
                            log["bos_level"] = bos_level
                            log["ep"] = ep
                            log["sl"] = sl
                            log["res"] = res
                            log['close_time'] = close_time
                            return log
                        is_fractal_now = is_fractal(day_dft[day_dft.index <= dt].tail(3))
                        if is_fractal_now is not None:
                            if is_fractal_now[1]:
                                bos_level = min(bos_level, float(is_fractal_now[2]))
                    else: 
                        log['setup'] = 'raid'
                        ep = row["close"]
                        sl = bos_level
                        log["ep"] = ep
                        log["sl"] = sl
                        log["ep_time"] = dt
                        res, close_time = ext_continue(full_df[full_df.index >= dt], ep, sl)
                        log["tp"] = ep + (ep - sl) * rr if ep > sl else ep - (sl - ep) * rr
                        log['res'] = res
                        log['close_time'] = close_time
                        return log

    log["res"] = None
    log["ep_time"] = None
    log["close_time"] = None
    return log


if __name__ == "__main__":
    df = pd.read_csv("data/feb02.csv", parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    
    # все дни список дат
    grouped = df.groupby(df.index.date)

    for date, day_df in grouped:
        full_df = df[df.index.date >= date]
        log = ext_setups(day_df, full_df)
        res = log["res"]
        if res is not None:
            # Подготовка параметров из словаря
            entry_time = pd.to_datetime(log["ep_time"])
            entry_price = log["ep"]
            stop_loss = log["sl"]
            take_profit = log["tp"]
            start_session = int(get_local_time_range(date)[0][:2])
            exit_time = pd.to_datetime(log['close_time'])
            df_context = get_slice_pos(df, entry_time, exit_time, start_hour=start_session)
            drawpos(
                df=df_context,
                entry_time=entry_time,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                exit_time=exit_time,
                session_start_hour=start_session
            )
        with open("logs.json", "a") as f:
            json.dump(log, f, indent=4, ensure_ascii=False, default=str)

