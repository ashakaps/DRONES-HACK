DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "drones",
    "user": "postgres",
    "password": "",
}

EXCEL_PATH = r"../data/data_clean.xlsx"
RUSSIA_GEOJSON = "./russia.geojson"
CITIES_GEOJSON = "./region_cities.geojson"

# название колонок
COLUMN_MAP = {
    "center": "center",
    "flight_id": "flight_id",
    "uav_type": "uav_type",
    "duration_min": "duration_min",
    "takeoff_lat": "takeoff_lat",
    "takeoff_lon": "takeoff_lon",
    "landing_lat": "landing_lat",
    "landing_lon": "landing_lon",
    "wind_dir": "wind_dir",
    "wind_speed": "wind_speed",
    "Т(С)": "temperature_c",  # температура
    "f(%)": "humidity_pct",  # влажность
    "dep_date": "dep_date",
    "dep_time": "dep_time",
    "arr_date": "arr_date",
    "arr_time": "arr_time",
    "season": "season",
    "air_traffic_load": "air_traffic_load",
    "traffic_cnt": "traffic_cnt",
    "relative_air_traffic_load": "relative_air_traffic_load",
    "distance": "distance",
    "speed": "speed",
}
