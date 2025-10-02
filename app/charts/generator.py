import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

DATA_FILE = os.path.join(os.path.dirname(__file__), "clean_data.xlsx")
PNG_DIR = "app/static/data/png"

FIG_SIZE = (6, 6)
DPI = 50

os.makedirs(PNG_DIR, exist_ok=True)

def safe_filename(name: str) -> str:
    """Превращает название города в безопасное имя файла"""
    return re.sub(r"[^a-zA-Z0-9а-яА-Я]", "_", name)

def generate_all_charts(city_name="Москва"):
    """Генерирует 3 графика и сохраняет в PNG_DIR"""
    df = pd.read_excel(DATA_FILE)

    # === Chart 1: Top-10 регионов ===
    top_regions = df["center"].value_counts().head(10)
    plt.figure(figsize=FIG_SIZE, dpi=DPI)
    if not top_regions.empty:
        regions = top_regions.index[::-1]
        counts = top_regions.values[::-1]
        bars = plt.barh(regions, counts, color=sns.color_palette("viridis", len(counts)))
        plt.bar_label(bars, labels=[str(int(v)) for v in counts], padding=3, fontsize=7)
    else:
        plt.text(0.5, 0.5, "Нет данных", ha="center", va="center", fontsize=12)
        plt.axis("off")
    plt.title("Топ-10 регионов", fontsize=10)
    plt.xlabel("Полёты", fontsize=8)
    plt.ylabel("Регион", fontsize=8)
    plt.tight_layout(pad=1.5)
    path_top = os.path.join(PNG_DIR, "top10_regions.png")
    plt.savefig(path_top, bbox_inches="tight")
    plt.close()

    # === Chart 2: Monthly totals ===
    path_monthly = os.path.join(PNG_DIR, "monthly_total.png")
    if "dep_datetime" in df.columns:
        df["dep_datetime"] = pd.to_datetime(df["dep_datetime"], errors="coerce", utc=True)
        df = df.dropna(subset=['dep_datetime']).copy()
        df['month'] = df['dep_datetime'].dt.to_period('M').astype(str)
        monthly_counts = df.groupby('month').size()

        plt.figure(figsize=FIG_SIZE, dpi=DPI)
        sns.barplot(x=monthly_counts.index, y=monthly_counts.values, color="steelblue")
        plt.title("DEBUG MONTHLY_TOTAL", fontsize=12, color="green")
        plt.xlabel("Месяц", fontsize=8)
        plt.ylabel("Количество", fontsize=8)
        plt.xticks(rotation=45, fontsize=7)
        plt.yticks(fontsize=7)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout(pad=1.5)
        plt.savefig(path_monthly, bbox_inches="tight")
        plt.close()

    # === Chart 3: Weekly by city (динамический) ===
    path_weekly = None
    if {"center", "dep_datetime"}.issubset(df.columns):
        df["dep_datetime"] = pd.to_datetime(df["dep_datetime"], errors="coerce", utc=True)
        df = df.dropna(subset=["dep_datetime", "center"]).copy()
        df_city = df[df["center"] == city_name]

        # уникальное имя файла для города
        safe_city = safe_filename(city_name)
        path_weekly = os.path.join(PNG_DIR, f"weekly_by_city_{safe_city}.png")

        # перед сохранением — удалить старые weekly_by_city_*.png
        for f in os.listdir(PNG_DIR):
            if f.startswith("weekly_by_city_"):
                try:
                    os.remove(os.path.join(PNG_DIR, f))
                except OSError:
                    pass

        plt.figure(figsize=FIG_SIZE, dpi=DPI)
        if df_city.empty:
            plt.text(0.5, 0.5, f"Нет данных\nдля {city_name}", ha="center", va="center", fontsize=12)
            plt.axis("off")
        else:
            df_city["week"] = df_city["dep_datetime"].dt.to_period("W").astype(str)
            weekly_counts = df_city.groupby("week").size()
            sns.barplot(x=weekly_counts.index, y=weekly_counts.values, color="coral")
            plt.xticks(rotation=45, fontsize=6)
            plt.yticks(fontsize=7)
        plt.title(f"Weekly by City ({city_name})", fontsize=10, color="red")
        plt.xlabel("Неделя", fontsize=8)
        plt.ylabel("Количество", fontsize=8)
        plt.tight_layout(pad=1.5)
        plt.savefig(path_weekly, bbox_inches="tight")
        plt.close()

    # возвращаем пути
    return {
        "top10_regions": "/static/data/png/top10_regions.png",
        "monthly_total": "/static/data/png/monthly_total.png",
        "weekly_by_city": f"/static/data/png/{os.path.basename(path_weekly)}" if path_weekly else None,
    }
