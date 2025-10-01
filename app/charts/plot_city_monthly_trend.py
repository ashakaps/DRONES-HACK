import os, io, base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_FILE = os.path.join(os.path.dirname(__file__), "clean_data.xlsx")
FIG_SIZE = (6, 6)
DPI = 100

def get_city_monthly_trend_plot(city_name="Москва"):
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Excel не найден: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE)
    if "center" not in df.columns or "dep_datetime" not in df.columns:
        raise ValueError("Нет колонок center или dep_datetime")

    df['dep_datetime'] = pd.to_datetime(df['dep_datetime'], errors="coerce", utc=True)
    df = df.dropna(subset=['dep_datetime', 'center'])
    df_city = df[df["center"] == city_name].copy()

    plt.figure(figsize=FIG_SIZE, dpi=DPI)
    plt.gca().set_facecolor("#e0f7fa")  # голубой фон
    if df_city.empty:
        plt.text(0.5, 0.5, f"Нет данных\nдля {city_name}", ha='center', va='center', fontsize=12)
        plt.axis('off')
        plt.title(f'DEBUG CITY_MONTHLY_TREND ({city_name})', fontsize=12, color="blue")
    else:
        df_city['date'] = df_city['dep_datetime'].dt.date
        daily_counts = df_city.groupby('date').size().reset_index(name='count')
        sns.lineplot(data=daily_counts, x='date', y='count',
                     marker='o', linewidth=2, color='green')
        plt.title(f'DEBUG CITY_MONTHLY_TREND ({city_name})', fontsize=12, color="blue")
        plt.xlabel('Дата', fontsize=8)
        plt.ylabel('Полёты', fontsize=8)
        plt.xticks(rotation=45, fontsize=6)
        plt.yticks(fontsize=7)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout(pad=1.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
