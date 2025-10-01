import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# путь к Excel рядом с этим файлом
DATA_FILE = os.path.join(os.path.dirname(__file__), "clean_data.xlsx")
FIG_SIZE = (6, 6)
DPI = 100

def get_monthly_total_plot():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Excel не найден: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE)
    if 'dep_datetime' not in df.columns:
        raise ValueError("Столбец 'dep_datetime' не найден")

    df['dep_datetime'] = pd.to_datetime(df['dep_datetime'], errors="coerce", utc=True)

    df = df.dropna(subset=['dep_datetime']).copy()
    df['month'] = df['dep_datetime'].dt.to_period('M').astype(str)

    monthly_counts = df.groupby('month').size()

    plt.figure(figsize=FIG_SIZE, dpi=DPI)
    sns.barplot(x=monthly_counts.index, y=monthly_counts.values, color='steelblue')
    plt.title('Полеты по месяцам', fontsize=10)
    plt.xlabel('Месяц', fontsize=8)
    plt.ylabel('Количество', fontsize=8)
    plt.xticks(rotation=45, fontsize=7)
    plt.yticks(fontsize=7)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout(pad=1.5)
    plt.title(f'ТЕСТ weekly_by_city ({city_name})', fontsize=10)
    plt.gca().set_facecolor("#f0f0f0")

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_base64
