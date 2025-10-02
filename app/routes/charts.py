from fastapi import APIRouter, Query
from app.charts.generator import generate_all_charts
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/{chart_name}")
def get_chart(chart_name: str, city: str = Query("Москва")):
    charts = generate_all_charts(city_name=city)
    if chart_name not in charts:
        return {"error": "Chart not found"}
    return {"path": charts[chart_name]}

@router.get("/report_json")
def report_json(city: str = Query("Москва")):
    """Возвращает те же данные, что и для графиков, но в JSON"""
    df = pd.read_excel(DATA_FILE)

    # 1) Топ-10 регионов
    top_regions = df["center"].value_counts().head(10).to_dict()

    # 2) Ежемесячный итог
    df["dep_datetime"] = pd.to_datetime(df["dep_datetime"], errors="coerce", utc=True)
    df = df.dropna(subset=["dep_datetime"])
    df["month"] = df["dep_datetime"].dt.to_period("M").astype(str)
    monthly_counts = df.groupby("month").size().to_dict()

    # 3) По выбранному городу
    df_city = df[df["center"] == city]
    if not df_city.empty:
        df_city["week"] = df_city["dep_datetime"].dt.to_period("W").astype(str)
        weekly_counts = df_city.groupby("week").size().to_dict()
    else:
        weekly_counts = {}

    report = {
        "city": city,
        "top10_regions": top_regions,
        "monthly_total": monthly_counts,
        "weekly_by_city": weekly_counts,
    }
    return JSONResponse(content=report)
