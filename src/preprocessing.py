import pandas as pd
import re
import os

# абсолютный путь к папке проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# путь к папке datasets
DATA_DIR = os.path.join(BASE_DIR, "datasets")

# читаем файлы
df_2024_per_city = pd.read_excel(
    os.path.join(DATA_DIR, "2024_v2.xlsx"), sheet_name=None
)
df_2025_per_city = pd.read_excel(
    os.path.join(DATA_DIR, "2025_v2.xlsx"), sheet_name=None
)


def add_center(data, district_name):
    return pd.concat(
        [pd.DataFrame([district_name] * len(data), columns=["center"]), data], axis=1
    )


df_combined = add_center(df_2024_per_city["Москва"], "Москва")
for key in list(df_2024_per_city.keys())[1:]:
    df_combined = pd.concat(
        [df_combined, add_center(df_2024_per_city[key], key)], ignore_index=True
    )
df_2024 = df_combined.copy()

df_2025 = pd.DataFrame()
for key in df_2025_per_city.keys():
    df_2025 = pd.concat(
        [df_2025, add_center(df_2025_per_city[key], key)], ignore_index=True
    )
    df_combined = pd.concat(
        [df_combined, add_center(df_2025_per_city[key], key)], ignore_index=True
    )

# id полета
df_combined["flight_id"] = df_combined["SHR"].str.extract(r"SID/(\d+)")
# тип БПЛА
df_combined["uav_type"] = df_combined["SHR"].str.extract(r"TYP/([^\s)]+)")
# координаты взлета
df_combined["dep_coord"] = df_combined["SHR"].str.extract(r"DEP/([0-9]+[NS][0-9]+[EW])")
# координаты посадки
df_combined["dest_coord"] = df_combined["SHR"].str.extract(
    r"DEST/([0-9]+[NS][0-9]+[EW])"
)
# плановая дата полета, формат - YYMMDD
df_combined["dof"] = df_combined["SHR"].str.extract(r"DOF/(\d{6})")

# плановое время полета по записям за 2024 (запись вида ARR - откуда и во сколько,куда и во сколько) формат - HHMM
times = df_combined["ARR"].str.extract(
    r"ARR-[A-Z0-9]+-[A-Z0-9]{4}(?P<dep_hhmm>\d{4})-[A-Z0-9]{4}(?P<arr_hhmm>\d{4})"
)
df_combined["dep_time_plan"] = times["dep_hhmm"]
df_combined["arr_time_plan"] = times["arr_hhmm"]

# по записям на 2025 - фактические даты и времени (поиск по DEP/ARR)
df_combined["dep_time_actual"] = None
df_combined["arr_time_actual"] = None
df_combined["dep_date_actual"] = None
df_combined["arr_date_actual"] = None
atd_series = df_2025["DEP"].astype(str).str.extract(r"ATD (\d{4})")[0]
ata_series = df_2025["ARR"].astype(str).str.extract(r"ATA (\d{4})")[0]
add_series = df_2025["DEP"].astype(str).str.extract(r"ADD (\d{6})")[0]
ada_series = df_2025["ARR"].astype(str).str.extract(r"ADA (\d{6})")[0]

# в случае отсутсвия ADD (фактическая дата вылета) записываем плановую дату (DOF)
# запись фактич даты и времени в датафрейм
offset_2025 = len(df_2024)
for idx in range(len(df_2025)):
    combined_idx = offset_2025 + idx
    dep_time = atd_series.iloc[idx]
    arr_time = ata_series.iloc[idx]
    dep_date = add_series.iloc[idx]
    arr_date = ada_series.iloc[idx]
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


# склеиваем даты вида YYMMDD и HHMM в pandas.Timestamp
def combine_date_time(date_str, time_str):
    if pd.isna(date_str) or pd.isna(time_str):
        return pd.NaT
    try:
        return pd.to_datetime(str(date_str) + str(time_str), format="%y%m%d%H%M")
    except Exception:
        return pd.NaT


# проходимся по рядам (фактич дата и время или плановые)
# вылет
df_combined["dep_datetime"] = df_combined.apply(
    lambda row: combine_date_time(
        row["dep_date_actual"] if pd.notna(row["dep_date_actual"]) else row["dof"],
        (
            row["dep_time_actual"]
            if pd.notna(row["dep_time_actual"])
            else row["dep_time_plan"]
        ),
    ),
    axis=1,
)
# прилет
df_combined["arr_datetime"] = df_combined.apply(
    lambda row: combine_date_time(
        row["arr_date_actual"] if pd.notna(row["arr_date_actual"]) else row["dof"],
        (
            row["arr_time_actual"]
            if pd.notna(row["arr_time_actual"])
            else row["arr_time_plan"]
        ),
    ),
    axis=1,
)

# обработка случая когда прилет произошел раньше по времени, чем вылет (добавляем сутки к прилету)
# ситуация разных часовых поясов
mask = (
    df_combined["dep_datetime"].notna()
    & df_combined["arr_datetime"].notna()
    & (df_combined["arr_datetime"] < df_combined["dep_datetime"])
)
df_combined.loc[mask, "arr_datetime"] += pd.Timedelta(days=1)

# работа с длительностью полета
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
    if len(lat_digits) == 4:  # DDMM
        lat_min = int(lat_digits[2:4])
        lat_sec = 0
    elif len(lat_digits) == 6:  # DDMMSS
        lat_min = int(lat_digits[2:4])
        lat_sec = int(lat_digits[4:6])
    else:
        lat_min = int(lat_digits[2:4]) if len(lat_digits) >= 4 else 0
        lat_sec = int(lat_digits[4:6]) if len(lat_digits) >= 6 else 0
    lat = lat_deg + lat_min / 60 + lat_sec / 3600
    if lat_hem == "S":
        lat = -lat
    if len(lon_digits) == 5:  # DDDMM
        lon_deg = int(lon_digits[0:3])
        lon_min = int(lon_digits[3:5])
        lon_sec = 0
    elif len(lon_digits) == 7:  # DDDMMSS
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
# взлет
df_combined[["takeoff_lat", "takeoff_lon"]] = df_combined["dep_coord"].apply(
    lambda c: pd.Series(parse_coordinate(c))
)
# посадка
df_combined[["landing_lat", "landing_lon"]] = df_combined["dest_coord"].apply(
    lambda c: pd.Series(parse_coordinate(c))
)

# обаботка координат для таблицы 2025 года (ARR по ключу ADARRZ)
missing_dest = df_combined["landing_lat"].isna() & df_combined["ARR"].notna()
for idx in df_combined[missing_dest].index:
    text = str(df_combined.at[idx, "ARR"])
    match = re.search(r"ADARRZ ([0-9]+[NS][0-9]+[EW])", text)
    if match:
        lat_val, lon_val = parse_coordinate(match.group(1))
        df_combined.at[idx, "landing_lat"] = lat_val
        df_combined.at[idx, "landing_lon"] = lon_val

df_final = df_combined.drop(
    columns=[
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
)
df_final.reset_index(drop=True, inplace=True)

# удаление записей - дубликатов по ключу dedup_key (уникальному сочетанию)
# пункт 3.2 ТЗ
df = df_final.copy()
mask_no_id = df["flight_id"].isna() | (df["flight_id"].astype(str).str.strip() == "")
df_with_id = df[~mask_no_id].copy()
df_no_id = df[mask_no_id].copy()
# удаление дублей с ключом flight_id + dep_date (записи с flight_id)
key_with_id = ["flight_id", "dep_datetime"]
df_with_id = df_with_id.sort_values(["flight_id", "dep_datetime"], kind="stable")
df_with_id = df_with_id.drop_duplicates(subset=key_with_id, keep="first")

# записи без flight_id
key_no_id = [
    "dep_datetime",
    "takeoff_lat",
    "takeoff_lon",
    "landing_lat",
    "landing_lon",
]
df_no_id = df_no_id.sort_values(["dep_datetime"], kind="stable")
df_no_id = df_no_id.drop_duplicates(subset=key_no_id, keep="first")
df_final = pd.concat([df_with_id, df_no_id], ignore_index=True)


df_final["year_month"] = df_final["dep_datetime"].dt.to_period("M").astype(str)
df_final["weekday"] = df_final["dep_datetime"].dt.dayofweek  # 0 - Monday
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

df_final.to_excel(
    os.path.join(os.path.join(BASE_DIR, "data"), "data.xlsx"), index=False
)
# df_final.to_csv(os.path.join(BASE_DIR, "data", "data.csv"), index=False)
