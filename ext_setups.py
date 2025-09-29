import pandas as pd
import logging
from local_time import get_local_time_range
from first_ext import first_ext
from check_test_ib import check_test_ib
from check_setup import check_setup
from ext_continue import ext_continue
from drawpos import drawpos


logging.basicConfig(
    filename="ext_setups.log",           # файл для логов
    level=logging.INFO,          # уровень логирования
    format="[%(levelname)s] %(message)s",  # формат строки
)


def main(day_df, full_df, rr=1):
    # дату и время иб определяем
    date = day_df.index[0].to_pydatetime()
    ib_start, ib_end, day_start, day_end = get_local_time_range(date)
    ib_set = day_df.between_time(ib_start, ib_end)
    min_ib, max_ib = ib_set["low"].min(), ib_set["high"].max()
    if ib_set.empty:
        return "ib not detected"
    logging.info(f"{date}  ib: {min_ib}-{max_ib}")

    day_dft = day_df.between_time(day_start, day_end)
    if day_dft.empty:
        return "day_df not detected"
    
    # Определяет, был ли первым пробой вверх (True), вниз (False) или его не было (None) за границы IB
    first_ext_direction = first_ext(
        min_ib=min_ib,
        max_ib=max_ib, 
        day_dft=day_dft
    )
    if first_ext_direction is None:
        return "no breakout IB"
    logging.info(f"{date} first ext direction {first_ext_direction}")

    # Определяет первый тест IB после выхода с фракталом; возвращает уровень фрактала и время свечи или None
    bos_level, bos_dt = check_test_ib(
        first_ext_direction=first_ext_direction,
        min_ib=min_ib,
        max_ib=max_ib,
        day_dft=day_dft
    )
    if bos_level is None:
        return "have not tested IB"
    logging.info(f"{date} bos level: {bos_level}, {bos_dt}")

    # true - ext, false - raid, none 
    setup, entry_time = check_setup(
        min_ib=min_ib,
        max_ib=max_ib,
        first_ext_direction=first_ext_direction,
        bos_level=bos_level,
        bos_dt=bos_dt,
        day_dft=day_dft
    )
    if setup is None:
        return "no entry"
    logging.info(f"{date} {setup} {entry_time}")


    if setup and first_ext_direction:
        res, close_dt = ext_continue(full_df[full_df.index >= entry_time], day_dft.loc[entry_time, "close"], min_ib, 1)
    elif setup:
        res, close_dt = ext_continue(full_df[full_df.index >= entry_time], day_dft.loc[entry_time, "close"], max_ib, 1)
    else:
        res, close_dt = ext_continue(full_df[full_df.index >= entry_time], day_dft.loc[entry_time, "close"], bos_level, 1)
    if res is not None:
        logging.info(f"{date} res: {res}, close: {close_dt}")    
    else:
        logging.info(f"{date} нет информации для тейка или стопа")



if __name__ == "__main__":
    df = pd.read_csv("data/feb.csv", parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    grouped = df.groupby(df.index.date)
    for date, day_df in grouped:
        full_df = df[df.index.date >= date]
        res = main(day_df=day_df, full_df=full_df)
        if isinstance(res, str):
            logging.info(res)
        logging.info("----- ------------------------------------------------------------------------")
