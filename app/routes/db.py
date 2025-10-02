import os
import shutil
import uuid
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.services import db
from database import load_all_data

router = APIRouter(prefix="/db", tags=["db"])

@router.get("/ping")
async def db_ping():
    ok, info = await db.ping()
    return {"ok": ok, "info": info}

@router.get("/status")
async def db_status():
    return await db.status()

@router.get("/flight_count")
async def db_flight_count():
    pool = await db.ensure_pool()
    async with pool.acquire() as conn:
        result = await conn.fetch("""
            SELECT count(1)
            FROM flight
        """)
        return {"flight_count": result[0][0]}
    
# Создаем папку /tmp если её нет
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Эндпоинт для загрузки файлов и запуска обработки
    """
    try:
        # Проверяем тип файла
        allowed_extensions = {'.xlsx'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
            )

        # Проверяем размер файла (максимум 100MB)
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        file.file.seek(0, 2)  # Переходим в конец файла
        file_size = file.file.tell()
        file.file.seek(0)  # Возвращаемся в начало
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB"
            )

        # Генерируем уникальное имя файла
        file_id = str(uuid.uuid4())
        original_filename = file.filename
        saved_filename = f"{file_id}_{original_filename}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Запускаем обработку в фоне
        background_tasks.add_task(process_uploaded_file, file_path, original_filename)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Файл успешно загружен и поставлен в очередь на обработку",
                "file_id": file_id,
                "filename": original_filename,
                "file_size": file_size
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        # Логируем ошибку
        print(f"Ошибка при загрузке файла: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Произошла ошибка при загрузке файла"
        )


async def process_uploaded_file(file_path: str, original_filename: str):
    """
    Фоновая задача для обработки загруженного файла
    """
    try:
        print(f"Начата обработка файла: {original_filename}")
        
        
        result = load_all_data.load_all_data(file_path)
        
        print(f"Обработка файла {original_filename} завершена. Результат: {result}")
        
        # Опционально: удаляем файл после обработки
        # os.remove(file_path)
        # print(f"Файл {file_path} удален после обработки")
        
    except Exception as e:
        # Логируем ошибку обработки
        error_msg = f"Ошибка при обработке файла {original_filename}: {str(e)}"
        print(error_msg)
        
        # Можно также сохранить ошибку в лог файл или БД




@router.get("/upload-status/{file_id}")
async def get_upload_status(file_id: str):
    """
    Эндпоинт для проверки статуса обработки файла
    (опционально, если нужно отслеживать статус)
    """
    # Здесь можно реализовать логику отслеживания статуса обработки
    # Например, хранить статусы в Redis или БД
    
    return {
        "file_id": file_id,
        "status": "processing",  # или "completed", "failed"
        "message": "Файл в процессе обработки"
    }