import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import matplotlib
matplotlib.use('Agg') 


def get_slice_pos(df, entry_time, exit_time, start_hour=10, extra_minutes=30):
    """
    Возвращает срез df от (дня входа в 10:00) до (exit_time + extra_minutes)
    """
    entry_time = pd.to_datetime(entry_time)
    exit_time = pd.to_datetime(exit_time)

    # Начало: день входа в 10:00
    start_time = entry_time.normalize() + pd.Timedelta(hours=start_hour)
    # Конец: время выхода + немного
    end_time = exit_time + pd.Timedelta(minutes=extra_minutes)

    return df.loc[start_time:end_time]


def drawpos(df, entry_time, entry_price, stop_loss, take_profit, exit_time,
            session_start_hour=10, extra_minutes=30):
    """
    Рисует сделку на свечном графике и подсвечивает первый торговый час как прямоугольник по цене.
    """

    # Создание папки для изображений
    os.makedirs("images", exist_ok=True)

    # Подготовка df
    df = df.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)

    # Определяем начало и конец отображаемого диапазона
    session_start = entry_time.normalize() + pd.Timedelta(hours=session_start_hour)
    session_end = session_start + pd.Timedelta(hours=1)
    chart_end = exit_time + pd.Timedelta(minutes=extra_minutes)

    # Отображаемая часть df
    df_window = df.loc[session_start:chart_end]

    # Настройка графика
    plt.figure(figsize=(12, 6))
    ax = plt.gca()

    # ===== 🎨 First Hour Rectangle (по ценам) =====
    df_first_hour = df.loc[session_start:session_end]

    if not df_first_hour.empty:
        price_low = df_first_hour['low'].min()
        price_high = df_first_hour['high'].max()

        # Небольшой отступ сверху/снизу (по желанию)
        padding_pct = 0.005
        price_range = price_high - price_low
        price_low -= price_range * padding_pct
        price_high += price_range * padding_pct

        rect = Rectangle(
            (session_start, price_low),
            session_end - session_start,
            price_high - price_low,
            facecolor="gray",
            alpha=0.4,
            edgecolor="gray",
            linewidth=0.5,
            zorder=0,
        )
        ax.add_patch(rect)

    # ===== 🕯️ Рисуем свечи =====
    for time, row in df_window.iterrows():
        color = 'green' if row['close'] >= row['open'] else 'red'
        # Тень свечи
        ax.plot([time, time], [row['low'], row['high']], color=color, zorder=1)
        # Тело свечи
        ax.add_patch(Rectangle(
            (time - pd.Timedelta(minutes=2.5), min(row['open'], row['close'])),
            pd.Timedelta(minutes=5),
            abs(row['close'] - row['open']),
            facecolor=color,
            edgecolor='black',
            linewidth=0.3,
            zorder=2
        ))

    # ===== 📉 Горизонтальные уровни =====
    ax.axhline(entry_price, color='blue', linestyle='--', label='Entry', linewidth=1)
    ax.axhline(stop_loss, color='red', linestyle='--', label='Stop Loss', linewidth=1)
    ax.axhline(take_profit, color='green', linestyle='--', label='Take Profit', linewidth=1)

    # ===== ⏱ Вертикальные линии =====
    # ax.axvline(entry_time, color='blue', linestyle=':', linewidth=1)
    try:
        ax.axvline(exit_time, color='black', linestyle=':', linewidth=1, label='Exit Time')
    except TypeError:
        ...
    # ===== 📍 Метки входа/выхода =====
    ax.plot(entry_time, entry_price, marker='^', color='blue', markersize=10, zorder=3)
    df_exit_row = df[df.index == exit_time]
    if not df_exit_row.empty:
        exit_price = df_exit_row.iloc[0]['close']
        ax.plot(exit_time, exit_price, marker='v', color='black', markersize=10, zorder=3)

    # ===== 🎚️ Стилизация =====
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    ax.set_title(f'Trade from {entry_time.strftime("%Y-%m-%d %H:%M")}')
    ax.set_ylabel('Price')
    ax.set_xlabel('Time')
    plt.grid(False)
    ax.legend(loc='lower right')

    # Сохраняем
    filename = f"images/{entry_time.strftime('%Y-%m-%d_%H-%M')}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    print(f"✅ Сделка сохранена как: {filename}")
