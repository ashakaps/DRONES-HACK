import sqlite3
import pandas as pd
from datetime import datetime

def create_database_tables(csv_file_path, db_file_path):
    """
    Создает базу данных SQLite из Excel/CSV файла с нормализованными таблицами
    """
    
    # Загрузка данных из CSV/Excel
    try:
        # Если файл Excel
        if csv_file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(csv_file_path)
        else:  # Если CSV
            df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return
    
    # Подключение к базе данных SQLite
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    
    # 1. Таблица центров ЕС ОрВД
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS centers (
        center_id INTEGER PRIMARY KEY AUTOINCREMENT,
        center_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 2. Таблица типов БПЛА
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS uav_types (
        uav_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        uav_type_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 3. Таблица сезонов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seasons (
        season_id INTEGER PRIMARY KEY AUTOINCREMENT,
        season_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 4. Таблица регионов (для загруженности воздушного движения)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS regions (
        region_id INTEGER PRIMARY KEY AUTOINCREMENT,
        region_name TEXT NOT NULL UNIQUE,
        area REAL,
        traffic_load REAL
    )
    ''')
    
    # 5. Основная таблица полетов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        flight_id TEXT PRIMARY KEY,
        center_id INTEGER,
        uav_type_id INTEGER,
        season_id INTEGER,
        region_id INTEGER,
        dep_datetime DATETIME,
        arr_datetime DATETIME,
        duration_min REAL,
        takeoff_lat REAL,
        takeoff_lon REAL,
        landing_lat REAL,
        landing_lon REAL,
        distance REAL,
        speed REAL,
        FOREIGN KEY (center_id) REFERENCES centers (center_id),
        FOREIGN KEY (uav_type_id) REFERENCES uav_types (uav_type_id),
        FOREIGN KEY (season_id) REFERENCES seasons (season_id),
        FOREIGN KEY (region_id) REFERENCES regions (region_id)
    )
    ''')
    
    # 6. Таблица погодных условий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_conditions (
        weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_id TEXT,
        wind_dir REAL,
        wind_speed REAL,
        temperature_c REAL,
        humidity_percent REAL,
        precipitation_mm REAL,
        FOREIGN KEY (flight_id) REFERENCES flights (flight_id)
    )
    ''')
    
    # 7. Таблица статистики воздушного движения
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS air_traffic_stats (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        region_id INTEGER,
        stat_date DATE,
        traffic_cnt INTEGER,
        air_traffic_load REAL,
        FOREIGN KEY (region_id) REFERENCES regions (region_id)
    )
    ''')
    
    # Заполнение справочных таблиц уникальными значениями
    try:
        # Центры
        unique_centers = df['center'].unique()
        for center in unique_centers:
            cursor.execute('INSERT OR IGNORE INTO centers (center_name) VALUES (?)', (center,))
        
        # Типы БПЛА
        unique_uav_types = df['uav_type'].unique()
        for uav_type in unique_uav_types:
            cursor.execute('INSERT OR IGNORE INTO uav_types (uav_type_name) VALUES (?)', (uav_type,))
        
        # Сезоны
        unique_seasons = df['season'].unique()
        for season in unique_seasons:
            cursor.execute('INSERT OR IGNORE INTO seasons (season_name) VALUES (?)', (season,))
        
        # Регионы (используем center как регион для упрощения)
        unique_regions = df['center'].unique()
        for region in unique_regions:
            # Берем среднюю загруженность для региона
            avg_load = df[df['center'] == region]['air_traffic_load'].mean()
            avg_traffic = df[df['center'] == region]['traffic_cnt'].mean()
            
            cursor.execute('''
            INSERT OR IGNORE INTO regions (region_name, traffic_load) 
            VALUES (?, ?)
            ''', (region, avg_load))
        
        # Получаем ID для связей
        center_ids = {row[1]: row[0] for row in cursor.execute('SELECT * FROM centers')}
        uav_type_ids = {row[1]: row[0] for row in cursor.execute('SELECT * FROM uav_types')}
        season_ids = {row[1]: row[0] for row in cursor.execute('SELECT * FROM seasons')}
        region_ids = {row[1]: row[0] for row in cursor.execute('SELECT * FROM regions')}
        
        # Заполнение основной таблицы полетов
        for index, row in df.iterrows():
            # Создаем datetime объекты
            dep_datetime = f"{row['dep_date']} {row['dep_time']}"
            arr_datetime = f"{row['arr_date']} {row['arr_time']}"
            
            cursor.execute('''
            INSERT OR REPLACE INTO flights (
                flight_id, center_id, uav_type_id, season_id, region_id,
                dep_datetime, arr_datetime, duration_min,
                takeoff_lat, takeoff_lon, landing_lat, landing_lon,
                distance, speed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['flight_id'],
                center_ids.get(row['center']),
                uav_type_ids.get(row['uav_type']),
                season_ids.get(row['season']),
                region_ids.get(row['center']),  # Используем center как регион
                dep_datetime,
                arr_datetime,
                row['duration_min'],
                row['takeoff_lat'],
                row['takeoff_lon'],
                row['landing_lat'],
                row['landing_lon'],
                row['distance'],
                row['speed']
            ))
            
            # Заполнение таблицы погодных условий
            cursor.execute('''
            INSERT INTO weather_conditions (
                flight_id, wind_dir, wind_speed, temperature_c, 
                humidity_percent, precipitation_mm
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row['flight_id'],
                row['wind_dir'],
                row['wind_speed'],
                row['Т(С)'],
                row['f(%)'],
                row['R(мм)']
            ))
        
        # Заполнение статистики воздушного движения
        # Группируем по дате и региону
        df['dep_date'] = pd.to_datetime(df['dep_date'])
        traffic_stats = df.groupby(['dep_date', 'center']).agg({
            'traffic_cnt': 'first',
            'air_traffic_load': 'first'
        }).reset_index()
        
        for index, row in traffic_stats.iterrows():
            cursor.execute('''
            INSERT INTO air_traffic_stats (
                region_id, stat_date, traffic_cnt, air_traffic_load
            ) VALUES (?, ?, ?, ?)
            ''', (
                region_ids.get(row['center']),
                row['dep_date'].strftime('%Y-%m-%d'),
                row['traffic_cnt'],
                row['air_traffic_load']
            ))
        
        conn.commit()
        print("База данных успешно создана и заполнена!")
        print(f"Создано таблиц: 7")
        print(f"Обработано записей: {len(df)}")
        
        # Вывод информации о таблицах
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nСозданные таблицы:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"- {table[0]}: {count} записей")
            
    except Exception as e:
        print(f"Ошибка при заполнении базы данных: {e}")
        conn.rollback()
    
    finally:
        conn.close()

def query_example(db_file_path):
    """Пример запроса к созданной базе данных"""
    conn = sqlite3.connect(db_file_path)
    
    # Пример сложного запроса с JOIN
    query = '''
    SELECT 
        f.flight_id,
        c.center_name,
        u.uav_type_name,
        s.season_name,
        f.dep_datetime,
        f.duration_min,
        w.wind_speed,
        w.temperature_c
    FROM flights f
    JOIN centers c ON f.center_id = c.center_id
    JOIN uav_types u ON f.uav_type_id = u.uav_type_id
    JOIN seasons s ON f.season_id = s.season_id
    JOIN weather_conditions w ON f.flight_id = w.flight_id
    LIMIT 5
    '''
    
    df_result = pd.read_sql_query(query, conn)
    print("\nПример данных из базы:")
    print(df_result)
    
    conn.close()

# Использование скрипта
if __name__ == "__main__":
    # Укажите путь к вашему файлу
    input_file = "data/data_new_features.xlsx"  # или .csv
    output_db = "uav_flights.db"
    
    # Создание базы данных
    create_database_tables(input_file, output_db)
    
    # Пример запроса
    query_example(output_db)