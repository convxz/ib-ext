import matplotlib
matplotlib.use('TkAgg')

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import mplfinance as mpf

# Загружаем данные
def load_data():
    df = pd.read_csv("data/march.csv", parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    return df


# Отрисовка графика
def plot_chart(parent, status_label):
    df = load_data()

    # Сохраняем индекс в список для обращения
    datetimes = df.index.to_list()

    # Создаём свечной график
    style = mpf.make_mpf_style(base_mpf_style="charles", rc={"font.size": 8})
    fig, axes = mpf.plot(
        df,
        type="candle",
        style=style,
        volume=False,
        returnfig=True,
        figsize=(9, 5),
        datetime_format="%H:%M",
    )

    ax = axes[0]

    # Вставляем график в tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Панель инструментов
    toolbar_frame = tk.Frame(parent)
    toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()

    # Обработчик мыши
    def on_mouse_move(event):
        if event.inaxes == ax:
            xdata = event.xdata
            if xdata is not None:
                try:
                    index = int(round(xdata))
                    if 0 <= index < len(datetimes):
                        date = datetimes[index]
                        status_label.config(text=f"Дата: {date.strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        status_label.config(text="Дата: -")
                except Exception:
                    status_label.config(text="Дата: Ошибка")
            else:
                status_label.config(text="Дата: -")
        else:
            status_label.config(text="Дата: -")

    canvas.mpl_connect("motion_notify_event", on_mouse_move)


# Главное окно
def main():
    root = tk.Tk()
    root.title("График с датой под курсором")
    root.geometry("1000x700")

    # Frame для графика
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    # Нижний статус
    status_frame = tk.Frame(root)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X)

    status_label = tk.Label(status_frame, text="Дата: -", anchor="e")
    status_label.pack(side=tk.RIGHT, padx=10, pady=5)

    plot_chart(frame, status_label)
    root.mainloop()


if __name__ == "__main__":
    main()