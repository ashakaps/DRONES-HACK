import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "clean_data.xlsx")
FIG_SIZE = (6, 6)
DPI = 100

def get_hourly_distribution_plot():
    df = pd.read_excel(DATA_FILE)
    if 'dep_datetime' not in df.columns:
        raise ValueError("Столбец 'dep_datetime' не найден")

    df['dep_datetime'] = pd.to_datetime(df['dep_datetime'], errors='coerce')
    df = df.dropna(subset=['dep_datetime']).copy()

    if df.empty:
        plt.figure(figsize=FIG_SIZE, dpi=DPI)
        plt.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=12)
        plt.axis('off')
        plt.title('Распределение по часам', fontsize=10)
    else:
        df['hour'] = df['dep_datetime'].dt.hour
        hourly_counts = df['hour'].value_counts().sort_index()

        plt.figure(figsize=FIG_SIZE, dpi=DPI)
        sns.barplot(x=hourly_counts.index, y=hourly_counts.values, color='purple')
        plt.title('Распределение по часам', fontsize=10)
        plt.xlabel('Час', fontsize=8)
        plt.ylabel('Полёты', fontsize=8)
        plt.xticks(fontsize=7)
        plt.yticks(fontsize=7)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout(pad=1.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_base64
