import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os, io, base64

DATA_FILE = os.path.join(os.path.dirname(__file__), "clean_data.xlsx")
FIG_SIZE = (6, 6)
DPI = 100

def get_top10_regions_bar_plot():
    df = pd.read_excel(DATA_FILE)

    if "center" not in df.columns:
        raise ValueError("Столбец 'center' не найден в данных")

    top_regions = df["center"].value_counts().head(10)

    plt.figure(figsize=FIG_SIZE, dpi=DPI)
    if top_regions.empty:
        plt.text(0.5, 0.5, "Нет данных", ha="center", va="center", fontsize=12)
        plt.axis("off")
        plt.title("Топ-10 регионов", fontsize=10)
    else:
        regions = top_regions.index[::-1]
        counts = top_regions.values[::-1]
        bars = plt.barh(regions, counts, color=sns.color_palette("viridis", len(counts)))
        plt.bar_label(bars, labels=[str(int(v)) for v in counts], padding=3, fontsize=7)
        plt.title("Топ-10 регионов", fontsize=10)
        plt.xlabel("Полёты", fontsize=8)
        plt.ylabel("Регион", fontsize=8)
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout(pad=1.5)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
