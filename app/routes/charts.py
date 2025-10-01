from fastapi import APIRouter, Query
from app.charts import CHARTS
import base64, os, traceback

router = APIRouter(prefix="/charts", tags=["charts"])

@router.get("/{chart_name}")
def get_chart(chart_name: str, city: str = Query(None)):
    if chart_name not in CHARTS:
        return {"error": "chart not found"}

    try:
        # собираем kwargs (на будущее, для графиков с city)
        kwargs = {}
        if city:
            kwargs["city"] = city

        # генерим картинку (base64)
        img_b64 = CHARTS[chart_name](**kwargs)

        # сохраняем как файл и отдаём путь
        out_dir = "app/static/data/png"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{chart_name}.png")

        with open(out_path, "wb") as f:
            f.write(base64.b64decode(img_b64))

        return {"path": f"/static/data/png/{chart_name}.png"}

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }
