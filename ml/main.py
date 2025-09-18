from fastapi import FastAPI

app = FastAPI(title="DroneRadar ML Service", version="0.1.0")

@app.get("/ping")
async def ping():
    return {"status": "ml-ok"}

@app.post("/predict")
async def predict(data: dict):
    # пока заглушка — просто возвращаем входные данные
    return {"prediction": "dummy", "input": data}
