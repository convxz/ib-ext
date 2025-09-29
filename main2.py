import pandas as pd
import json
from drawpos import drawpos, get_slice_pos
from is_fractal import is_fractal
from local_time import get_local_time_range
from ext_continue import ext_continue


def first_ext(min_ib, max_ib, day_dft):
    first_ext_direction = None
    for _, row in day_dft.iterrows():
        if row["high"] > max_ib:
            first_ext_direction = True
            return first_ext_direction
        elif row["low"] < min_ib:
            first_ext_direction = False
            return first_ext_direction
    return first_ext_direction


def check_test_ib(first_ext_direction, min_ib, max_ib, day_dft):
    if first_ext_direction is not None:
        if first_ext_direction:
            
            

def ext_setups(day_df, full_df, rr=1):
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
    # дату и время иб определяем
    date = day_df.index[0].to_pydatetime()
    ib_start, ib_end, day_start, day_end = get_local_time_range(date)
    ib_set = day_df.between_time(ib_start, ib_end)
    min_ib, max_ib = ib_set["low"].min(), ib_set["high"].max()
    day_dft = day_df.between_time(day_start, day_end)

    first_ext_direction = first_ext(
        min_ib=min_ib,
        max_ib=max_ib,
        day_dft=day_dft
    )
    ib_tested = None




if __name__ == "__main__":
    df = pd.read_csv("data/feb02.csv", parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    grouped = df.groupby(df.index.date)
    for date, day_df in grouped:
        full_df = df[df.index.date >= date]
        ext_setups(
            day_df=day_df,
            full_df=full_df  
        )