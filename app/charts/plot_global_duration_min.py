import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os, io, base64
import sqlite3

DB_FILE = os.path.join(os.path.dirname(__file__), "../datasets/uav_flights.db")
FIG_SIZE = (6, 6)
DPI = 100

def get_global_duration_min():
    sql = """
        SELECT 
            c.center_name AS center,
            s.season_name AS season,
            AVG(f.duration_min) AS mean_duration
        FROM flights f
        JOIN centers c ON f.center_id = c.center_id
        JOIN seasons s ON f.season_id = s.season_id
        GROUP BY c.center_name, s.season_name
        ORDER BY c.center_name, s.season_name;
    """

    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql(sql, conn)

    if df.empty:
        plt.figure(figsize=FIG_SIZE, dpi=DPI)
        plt.text(0.5, 0.5, "Нет данных", ha="center", va="center", fontsize=12)
        plt.axis("off")
        plt.title("Средняя длительность полётов", fontsize=10)
    else:
        df["season"] = df["season"].map(
            {"autumn": "Осень", "spring": "Весна", "summer": "Лето", "winter": "Зима"}
        )

        g = sns.catplot(
            data=df,
            x="season", y="mean_duration",
            col="center",
            kind="bar",
            col_wrap=3,
            height=4, aspect=1,
            sharex=False, sharey=False,
            palette="Set2"
        )
        g.set_titles("{col_name}")
        g.set_axis_labels("Время года", "Средняя длительность полёта (мин)")
        plt.subplots_adjust(top=0.9)
        plt.suptitle("Средняя длительность полётов по сезонам и центрам")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
