import os, io, base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_FILE = os.path.join(os.path.dirname(__file__), "clean_data.xlsx")
FIG_SIZE = (6, 6)
DPI = 100

def get_weekly_by_city_plot(city_name="Москва"):
    df = pd.read_excel(DATA_FILE)
    for col in ['center', 'dep_datetime']:
        if col not in df.columns:
            raise ValueError(f"Столбец '{col}' не найден")

    df['dep_datetime'] = pd.to_datetime(df['dep_datetime'], errors="coerce", utc=True)
    df = df.dropna(subset=['dep_datetime', 'center']).copy()
    df_city = df[df['center'] == city_name].copy()

    plt.figure(figsize=FIG_SIZE, dpi=DPI)
    plt.gca().set_facecolor("#f0f0f0")  # серый фон
    if df_city.empty:
        plt.text(0.5, 0.5, f"Нет данных\nдля {city_name}", ha='center', va='center', fontsize=12)
        plt.axis('off')
        plt.title(f'DEBUG WEEKLY_BY_CITY ({city_name})', fontsize=12, color="red")
    else:
        df_city['week'] = df_city['dep_datetime'].dt.to_period('W').astype(str)
        weekly_counts = df_city.groupby('week').size()
        sns.barplot(x=weekly_counts.index, y=weekly_counts.values, color='coral')
        plt.title(f'DEBUG WEEKLY_BY_CITY ({city_name})', fontsize=12, color="red")
        plt.xlabel('Неделя', fontsize=8)
        plt.ylabel('Количество', fontsize=8)
        plt.xticks(rotation=45, fontsize=6)
        plt.yticks(fontsize=7)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout(pad=1.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
