import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "clean_data.xlsx")
FIG_SIZE = (6, 6)
DPI = 100

def get_top10_regions_plot():
    df = pd.read_excel(DATA_FILE)
    if 'center' not in df.columns:
        raise ValueError("Столбец 'center' не найден")

    df = df.dropna(subset=['center']).copy()
    region_counts = df['center'].value_counts().head(10)

    if region_counts.empty:
        plt.figure(figsize=FIG_SIZE, dpi=DPI)
        plt.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=12)
        plt.axis('off')
        plt.title('ТОП-10 регионов', fontsize=10)
    else:
        plt.figure(figsize=FIG_SIZE, dpi=DPI)
        sns.barplot(x=region_counts.values, y=region_counts.index, palette='viridis')
        plt.title('ТОП-10 регионов', fontsize=10)
        plt.xlabel('Полёты', fontsize=8)
        plt.ylabel('Регион', fontsize=8)
        plt.xticks(fontsize=7)
        plt.yticks(fontsize=7)
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout(pad=1.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_base64
