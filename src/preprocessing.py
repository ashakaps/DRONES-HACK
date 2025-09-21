import os
import re
import pandas as pd

# абсолютный путь к папке проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# путь к папке datasets
DATA_DIR = os.path.join(BASE_DIR, "datasets")

# проверка наличия исходных файлов
path_2024 = os.path.join(DATA_DIR, "2024_v2.xlsx")
path_2025 = os.path.join(DATA_DIR, "2025_v2.xlsx")
if not os.path.exists(path_2024):
    raise FileNotFoundError(f"не найден файл: {path_2024}")
if not os.path.exists(path_2025):
    raise FileNotFoundError(f"не найден файл: {path_2025}")

# читаем файлы (каждый лист — это центр)
df_2024_per_city = pd.read_excel(path_2024, sheet_name=None, engine="openpyxl")
df_2025_per_city = pd.read_excel(path_2025, sheet_name=None, engine="openpyxl")


# вспомогательная функция
def add_center(data, district_name):
    return pd.concat(
        [pd.DataFrame([district_name] * len(data), columns=["center"]), data], axis=1
    )


# формируем 2024
_2024_parts = []
for key in df_2024_per_city.keys():
    _2024_parts.append(add_center(df_2024_per_city[key], key))
df_combined = pd.concat(_2024_parts, ignore_index=True)
df_2024 = df_combined.copy()

# формируем 2025 и добавляем к общему
_2025_parts = []
for key in df_2025_per_city.keys():
    _2025_parts.append(add_center(df_2025_per_city[key], key))
df_2025 = pd.concat(_2025_parts, ignore_index=True)
df_combined = pd.concat([df_combined, df_2025], ignore_index=True)

# заранее компилируем регулярки
_re_sid = re.compile(r"SID/(\d+)")
_re_typ = re.compile(r"TYP/([^\s)]+)")
_re_dep = re.compile(r"DEP/([0-9]+[NS][0-9]+[EW])")
_re_dest = re.compile(r"DEST/([0-9]+[NS][0-9]+[EW])")
_re_dof = re.compile(r"DOF/(\d{6})")
_re_arr = re.compile(
    r"ARR-[A-Z0-9]+-[A-Z0-9]{4}(?P<dep_hhmm>\d{4})-[A-Z0-9]{4}(?P<arr_hhmm>\d{4})"
)
_re_atd = re.compile(r"ATD (\d{4})")
_re_ata = re.compile(r"ATA (\d{4})")
_re_add = re.compile(r"ADD (\d{6})")
_re_ada = re.compile(r"ADA (\d{6})")
_re_adarrz = re.compile(r"ADARRZ ([0-9]+[NS][0-9]+[EW])")

# id полета
df_combined["flight_id"] = df_combined["SHR"].astype(str).str.extract(_re_sid)
# тип бпла
df_combined["uav_type"] = df_combined["SHR"].astype(str).str.extract(_re_typ)
# координаты взлета
df_combined["dep_coord"] = df_combined["SHR"].astype(str).str.extract(_re_dep)
# координаты посадки
df_combined["dest_coord"] = df_combined["SHR"].astype(str).str.extract(_re_dest)
# плановая дата полета, формат - yymmdd
df_combined["dof"] = df_combined["SHR"].astype(str).str.extract(_re_dof)

# плановые времена по шаблону из arr для 2024
times = df_combined["ARR"].astype(str).str.extract(_re_arr)
df_combined["dep_time_plan"] = times.get("dep_hhmm")
df_combined["arr_time_plan"] = times.get("arr_hhmm")

# фактические даты/времена по 2025
df_combined["dep_time_actual"] = None
df_combined["arr_time_actual"] = None
df_combined["dep_date_actual"] = None
df_combined["arr_date_actual"] = None

atd_series = (
    df_2025.get("DEP", pd.Series(dtype=object)).astype(str).str.extract(_re_atd)[0]
)
ata_series = (
    df_2025.get("ARR", pd.Series(dtype=object)).astype(str).str.extract(_re_ata)[0]
)
add_series = (
    df_2025.get("DEP", pd.Series(dtype=object)).astype(str).str.extract(_re_add)[0]
)
ada_series = (
    df_2025.get("ARR", pd.Series(dtype=object)).astype(str).str.extract(_re_ada)[0]
)

# записываем факты в общую таблицу (счёт в df_combined начинается после блока 2024)
offset_2025 = len(df_2024)
for idx in range(len(df_2025)):
    combined_idx = offset_2025 + idx
    dep_time = atd_series.iloc[idx] if idx < len(atd_series) else None
    arr_time = ata_series.iloc[idx] if idx < len(ata_series) else None
    dep_date = add_series.iloc[idx] if idx < len(add_series) else None
    arr_date = ada_series.iloc[idx] if idx < len(ada_series) else None
    if pd.isna(dep_date):
        dep_date = df_combined.loc[combined_idx, "dof"]
    if pd.notna(dep_date):
        df_combined.at[combined_idx, "dep_date_actual"] = dep_date
    if pd.notna(dep_time):
        df_combined.at[combined_idx, "dep_time_actual"] = dep_time
    if pd.notna(arr_date):
        df_combined.at[combined_idx, "arr_date_actual"] = arr_date
    if pd.notna(arr_time):
        df_combined.at[combined_idx, "arr_time_actual"] = arr_time

# склеиваем даты/времена векторно (nat допустим дальше в расчётах)
dep_date_src = df_combined["dep_date_actual"].where(
    df_combined["dep_date_actual"].notna(), df_combined["dof"]
)
dep_time_src = df_combined["dep_time_actual"].where(
    df_combined["dep_time_actual"].notna(), df_combined["dep_time_plan"]
)
arr_date_src = df_combined["arr_date_actual"].where(
    df_combined["arr_date_actual"].notna(), df_combined["dof"]
)
arr_time_src = df_combined["arr_time_actual"].where(
    df_combined["arr_time_actual"].notna(), df_combined["arr_time_plan"]
)

dep_dt_str = dep_date_src.astype(str) + dep_time_src.astype(str)
arr_dt_str = arr_date_src.astype(str) + arr_time_src.astype(str)

df_combined["dep_datetime"] = pd.to_datetime(
    dep_dt_str, format="%y%m%d%H%M", errors="coerce"
)
df_combined["arr_datetime"] = pd.to_datetime(
    arr_dt_str, format="%y%m%d%H%M", errors="coerce"
)

# обработка случая когда прилет раньше вылета (разные чп)
mask_flip = (
    df_combined["dep_datetime"].notna()
    & df_combined["arr_datetime"].notna()
    & (df_combined["arr_datetime"] < df_combined["dep_datetime"])
)
df_combined.loc[mask_flip, "arr_datetime"] = df_combined.loc[
    mask_flip, "arr_datetime"
] + pd.Timedelta(days=1)

# длительность полета (в минутах)
df_combined["duration_min"] = None
mask_duration = (
    df_combined["dep_datetime"].notna() & df_combined["arr_datetime"].notna()
)
df_combined.loc[mask_duration, "duration_min"] = (
    df_combined.loc[mask_duration, "arr_datetime"]
    - df_combined.loc[mask_duration, "dep_datetime"]
).dt.total_seconds() / 60


# перевод координат вида 554529N0382503E в градусы
def parse_coordinate(coord_str):
    if not isinstance(coord_str, str) or coord_str.strip() == "":
        return None, None
    match = re.match(r"^([0-9]+)([NS])([0-9]+)([EW])$", coord_str.strip())
    if not match:
        return None, None
    lat_digits, lat_hem, lon_digits, lon_hem = match.groups()
    lat_deg = int(lat_digits[0:2])
    if len(lat_digits) == 4:  # ddmm
        lat_min = int(lat_digits[2:4])
        lat_sec = 0
    elif len(lat_digits) == 6:  # ddmmss
        lat_min = int(lat_digits[2:4])
        lat_sec = int(lat_digits[4:6])
    else:
        lat_min = int(lat_digits[2:4]) if len(lat_digits) >= 4 else 0
        lat_sec = int(lat_digits[4:6]) if len(lat_digits) >= 6 else 0
    lat = lat_deg + lat_min / 60 + lat_sec / 3600
    if lat_hem == "S":
        lat = -lat
    if len(lon_digits) == 5:  # dddmm
        lon_deg = int(lon_digits[0:3])
        lon_min = int(lon_digits[3:5])
        lon_sec = 0
    elif len(lon_digits) == 7:  # dddmmss
        lon_deg = int(lon_digits[0:3])
        lon_min = int(lon_digits[3:5])
        lon_sec = int(lon_digits[5:7])
    else:
        lon_deg = int(lon_digits[0:3]) if len(lon_digits) >= 3 else int(lon_digits)
        lon_min = int(lon_digits[3:5]) if len(lon_digits) >= 5 else 0
        lon_sec = int(lon_digits[5:7]) if len(lon_digits) >= 7 else 0
    lon = lon_deg + lon_min / 60 + lon_sec / 3600
    if lon_hem == "W":
        lon = -lon
    return lat, lon


# преобразуем координаты
df_combined[["takeoff_lat", "takeoff_lon"]] = df_combined["dep_coord"].apply(
    lambda c: pd.Series(parse_coordinate(c))
)
df_combined[["landing_lat", "landing_lon"]] = df_combined["dest_coord"].apply(
    lambda c: pd.Series(parse_coordinate(c))
)

# обработка координат по ключу adarrz (для части записей 2025)
missing_dest = df_combined["landing_lat"].isna() & df_combined["ARR"].notna()
for idx in df_combined[missing_dest].index:
    text = str(df_combined.at[idx, "ARR"])
    m = _re_adarrz.search(text)
    if m:
        lat_val, lon_val = parse_coordinate(m.group(1))
        df_combined.at[idx, "landing_lat"] = lat_val
        df_combined.at[idx, "landing_lon"] = lon_val

# финальная таблица: выбрасываем служебные поля
to_drop = [
    "SHR",
    "DEP",
    "ARR",
    "dof",
    "dep_coord",
    "dest_coord",
    "dep_time_plan",
    "arr_time_plan",
    "dep_time_actual",
    "arr_time_actual",
    "dep_date_actual",
    "arr_date_actual",
]
df_final = df_combined.drop(
    columns=[c for c in to_drop if c in df_combined.columns]
).reset_index(drop=True)

# удаление записей - дубликатов по ключу (п. 3.2 тз)
df = df_final.copy()
mask_no_id = df["flight_id"].isna() | (df["flight_id"].astype(str).str.strip() == "")
df_with_id = df[~mask_no_id].copy()
df_no_id = df[mask_no_id].copy()

# записи с flight_id: считаем уникальным (flight_id, dep_datetime)
key_with_id = ["flight_id", "dep_datetime"]
df_with_id = df_with_id.sort_values(["flight_id", "dep_datetime"], kind="stable")
df_with_id = df_with_id.drop_duplicates(subset=key_with_id, keep="first")

# записи без flight_id: считаем уникальным (dep_datetime + координаты)
key_no_id = ["dep_datetime", "takeoff_lat", "takeoff_lon", "landing_lat", "landing_lon"]
df_no_id = df_no_id.sort_values(["dep_datetime"], kind="stable")
df_no_id = df_no_id.drop_duplicates(subset=key_no_id, keep="first")

df_final = pd.concat([df_with_id, df_no_id], ignore_index=True)

# производные временные поля
df_final["year_month"] = df_final["dep_datetime"].dt.to_period("M")
df_final["year_month"] = (
    df_final["year_month"].astype(str).where(df_final["dep_datetime"].notna(), None)
)
df_final["weekday"] = df_final["dep_datetime"].dt.dayofweek  # 0 - monday
df_final["date"] = df_final["dep_datetime"].dt.date
df_final["hour"] = df_final["dep_datetime"].dt.hour


# функция определения категории времени - утра/дня/вечера или ночи
def daypart(h):
    if pd.isna(h):
        return None
    h = int(h)
    if 6 <= h < 12:
        return "morning"
    if 12 <= h < 18:
        return "day"
    if 18 <= h < 24:
        return "evening"
    return "night"


df_final["daypart"] = df_final["hour"].apply(daypart)

# nat -> None
# for col in ["dep_datetime", "arr_datetime"]:
#     # формат строки можно поменять при желании (например, "%Y-%m-%d %H:%M:%S")
#     df_final[col] = df_final[col].dt.strftime("%Y-%m-%d %H:%M:%S").where(
#         df_final[col].notna(), None
#     )

# сохраняем в csv
out_dir = os.path.join(BASE_DIR, "data")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "data.xlsx")
df_final.to_excel(out, index=False)
