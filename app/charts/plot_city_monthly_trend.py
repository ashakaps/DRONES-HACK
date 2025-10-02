import os
import io
import base64
import pandas as pd

# важно: backend без GUI
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Excel лежит рядом с этим файлом
DATA_FILE = os.path.join(os.path.dirname(__file__), "clean_data.xlsx")
FIG_SIZE = (6, 6)
DPI = 100

def get_monthly_total_plot():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Excel не найден: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE)
    if "dep_datetime" not in df.columns:
        raise ValueError("Столбец 'dep_datetime' не найден")

    # парсим даты; без таймзоны (были проблемы от tz)
    df["dep_datetime"] = pd.to_datetime(df["dep_datetime"], errors="coerce")
    df = df.dropna(subset=["dep_datetime"]).copy()

    # группируем по месяцам
    df["month"] = df["dep_datetime"].dt.to_period("M").astype(str)
    monthly_counts = df.groupby("month").size().sort_index()

    # рисуем
    plt.figure(figsize=FIG_SIZE, dpi=DPI)
    sns.barplot(x=list(monthly_counts.index), y=list(monthly_counts.values), color="steelblue")
    plt.title("Полёты по месяцам", fontsize=11)
    plt.xlabel("Месяц", fontsize=9)
    plt.ylabel("Количество", fontsize=9)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout(pad=1.2)

    # в base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
