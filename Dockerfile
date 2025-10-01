# Этап 1: Сборка фронтенда
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Копируем package файлы фронтенда
COPY app/frontend/package*.json ./frontend/

WORKDIR /app/frontend

# Устанавливаем зависимости
RUN npm ci

# Копируем исходники фронтенда
COPY app/frontend/ ./

# Собираем фронтенд
RUN npm run build

# Этап 2: Финальный образ с бэкендом
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости если нужны
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем Python зависимости
COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY . .

# Копируем собранный фронтенд из первого этапа
COPY --from=frontend-builder /app/frontend/dist ./app/static

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
