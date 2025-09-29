import pytz
from datetime import datetime, date, time

def is_dst(dt, tz_name):
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, time.min)

    tz = pytz.timezone(tz_name)
    localized = tz.localize(dt, is_dst=None)
    return bool(localized.dst())


def get_local_time_range(dt):
    """
    Возвращает пару времён ("HH:MM", "HH:MM") в зависимости от DST в Берлине и Чикаго:
      - ("01:00", "02:00"): оба в зимнем времени
      - ("02:00", "03:00"): только одна зона в летнем времени
      - ("01:00", "01:00"): обе в летнем времени
    """
    berlin_dst = is_dst(dt, 'Europe/Berlin')
    chicago_dst = is_dst(dt, 'America/Chicago')

    if not berlin_dst and not chicago_dst:
        return ("01:00", "01:59", "01:55", "14:57")
    elif berlin_dst and chicago_dst:
        return ("01:00", "01:59", "01:55", "14:57")
    else:
        return ("02:00", "02:00", "02:55", "14:57")


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("data/march.csv", parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    grouped = df.groupby(df.index.date)
    for dt, day_df in grouped:
        print(dt, get_local_time_range(dt))