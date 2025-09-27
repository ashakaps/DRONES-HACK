# Заметка 1: нужно подумтаь над считыванием входных файлов разных типов либо же проработать ошибки которые будут возвращаться. 
# Заметка 2: нужно подроюить try except в инициализации класса на что-то поменьше

# --------------- Импорты ---------------
import pandas as pd
from os import walk
import numpy as np
import math
from collections import defaultdict
import re

from weather_parser import parser
# ---------------------------------------

class DataLoader:

    DATA_PATH = "D://hack/DRONES_HACK/data/" # путь к "сырым" данным
    DATA_NAME = next(walk(DATA_PATH), (None, None, []))[2] # имя "сырых" данных
    PREPOC_DATA_PATH = "D://hack/DRONES_HACK/datasets/" # путь готовых данных
    PREPOC_DATA_NAME = "data_weather_prepoc.xlsx" # имя готовых данных
    DEP_NAME = "dep_datetime"
    ARR_NAME = "arr_datetime"
    INDEX_WEATHER_NAME = "date"
    CITY_NAME = "center"
    FEATURES_MASK = ["wind_dir", "wind_speed", "Т(С)", "f(%)"] # набор погодных параметров  
    REGION_AREA_BY_CITY = { # примерная площадь регионов пеерчисленных столиц
        "Тюмень": 1464173,            
        "Москва": 2561.5,             
        "Красноярск": 2_366_797,      
        "Магадан": 462_464,           
        "Якутск": 3_083_523,          
        "Иркутск": 774_846,           
        "Новосибирск": 177_756,       
        "Ростов": 100_967,            
        "Екатеринбург": 194_307,      
        "Калининград": 15_125,        
        "Санкт-Петербург": 1_403,     
        "Самара": 53_565,              
        "Хабаровск": 787_633,          
        "Симферополь": 26_081         
    }

    def __add_center(self, data: pd.DataFrame, district_name: str) -> pd.DataFrame:
        return pd.concat(
            [pd.DataFrame([district_name] * len(data), columns=["center"]),
            data],
            axis = 1
        )
    
    def __combine_date_time(self, date_str: str, time_str: str) -> pd.Timestamp:
        if pd.isna(date_str) or pd.isna(time_str):
            return pd.NaT
        try:
            return pd.to_datetime(date_str + time_str, format="%y%m%d%H%M")
        except Exception:
            return pd.NaT
        
    def __parse_coordinate(self, coord_str: str) -> tuple:
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
    
    # Функция конверитрует дату и время в отдельные наборы
    def __get_data_info(self, idx: int, col: str) -> tuple:
        datatime = str(self.data.loc[idx, col])
        date, time = datatime.split()
        return (map(int, date.split('-')), map(int, time.split(":")))
    
    def __add_weather_features(self, idx: int, weather_data):
        # Получаю час взлета и посадки конкретного дрона 
        hour_dep, _, _ = self.__get_data_info(idx, self.DEP_NAME)[1]
        hour_arr, _, _ = self.__get_data_info(idx, self.ARR_NAME)[1]
        # Получаю год, месяц, день конкретного дрона
        y_dep, m_dep, d_dep = self.__get_data_info(idx, self.DEP_NAME)[0]
        y_arr, m_arr, d_arr = self.__get_data_info(idx, self.ARR_NAME)[0]
        # функция для доабвлению 0, чтоыб числа от 1-9 записывались как 01 и т.д
        add_zero = lambda num: f"0{num}" if len(str(num)) == 1 else num
        # Формирую диапозон который возьму ид дате о погоде 
        # при этом, так как значения идут сторого с шагом 3, все неподходящие я преобразую так: hour_dep // 3) * 3
        weather_data_idx_dep = f"{y_dep}.{add_zero(d_dep)}.{add_zero(m_dep)} {add_zero((hour_dep // 3) * 3)}"
        weather_data_idx_arr = f"{y_arr}.{add_zero(d_arr)}.{add_zero(m_arr)} {add_zero((hour_arr // 3) * 3)}"
        try:
            # Получаю нужные данные на добавление
            weather_data_for_item = weather_data.loc[weather_data_idx_dep:weather_data_idx_arr] 
            # Не все типы одинаковые, потому проходусь циклом по всем фичам и применяю либо моду для категориальных, лиюо среднее для числовых
            weather_info = weather_data_for_item.dtypes
            for col_name, dtype in zip(weather_info.index, weather_info):
                if dtype == "object":
                    self.data.loc[idx, col_name] = weather_data_for_item[col_name].mode().iloc[0]
                else: 
                    self.data.loc[idx, col_name] = weather_data_for_item[col_name].mean()
        except:
            pass

    def __pars_weather(self) -> None:
        # Обрабатываю каждый уникальный город
        for center in self.centers:
            # Получаю только записи нужного города, в которых указаны время взлёта и посадки
            dataset_center_idx = self.data[
                (self.data[self.CITY_NAME] == center) & 
                (self.data[self.DEP_NAME].notna() & self.data[self.ARR_NAME].notna())
            ].index.to_list()
            # Получаю самую первую дату
            y_f, m_f, _ = self.__get_data_info(
                dataset_center_idx[0], 
                self.DEP_NAME
            )[0]
            # Получаю самую последнюю
            y_l, m_l, _ = self.__get_data_info(
                dataset_center_idx[-1], 
                self.DEP_NAME
            )[0]
            # Теперь вытаскиваю данные за все нудные года и месяцы, идя от _f до _l
            weather_data = pd.concat(
                [
                    parser(year, range(1, m_l + 1) if year == y_l else range(1, 12 + 1), center)
                    for year in range(y_f, y_l + 1)
                ]
            ).set_index(self.INDEX_WEATHER_NAME)
            # Избавляюсь от multiindex
            weather_data.columns = [col[0] for col in weather_data.columns]
            weather_data.index = [idx[0] for idx in weather_data.index]
            # Все фичи кроме первой (которая категориальная) превращаю в числовые
            for feature in self.FEATURES_MASK[1:]:
                weather_data[feature] = pd.to_numeric(weather_data[feature], errors="coerce")
            # для каждой записи нахожу... или нет, нкжные данные
            for idx in dataset_center_idx:
                self.__add_weather_features(idx, weather_data[self.FEATURES_MASK])

            print(f"{center} parsed")

    def __get_season(self, month: int) -> str:
        if month in [12, 1, 2]: return 'winter'
        elif month in [3, 4, 5]: return 'spring'
        elif month in [6, 7, 8]: return 'summer'
        else: return 'autumn'

    def __init__(self) -> None:

        self.centers = set() # множество всех городов
        self.data = pd.DataFrame()

        # Считываю файлы 
        for item in self.DATA_NAME:
            # Проверка на возможность считать файл (в excel могут замешаться другие форматы) и т.д
            try:
                # Считываю данные из каждого файла
                raw_data = pd.read_excel(
                    self.DATA_PATH + item, 
                    sheet_name=None
                )
                # Получаю список городов 
                centers = list(raw_data.keys())
                # Заполняю множество уникальных городов о которых есть данные
                self.centers.update(centers)
                # Объединяю данные, добавляя метку из какого запись города
                for center in centers:
                    self.data = pd.concat(
                        [
                            self.data,
                            self.__add_center(raw_data[center], center)
                        ],
                        ignore_index=True
                    )
            except Exception as err:
                print(err)
                raise

    def __normalize_drone_type(self, x: str):
        if pd.isna(x):
            return np.nan
        x = str(x).upper()
        x = re.sub(r'[^A-ZА-Я]', '', x)
        # выделяю базовое название
        if 'BLA' in x:
            return 'BLA'
        elif 'AER' in x:
            return 'AER'
        elif 'DJI' in x:
            return 'DJI'
        elif 'ORLAN' in x:
            return 'ORLAN'
        elif 'FANTOM' in x:
            return 'FANTOM'
        elif 'SHAR' in x:
            return 'SHAR'
        elif 'КВАДРОКОПТЕР' in x:
            return 'BLA'
        elif 'BWS' in x:
            return 'BWS'
        elif " ":
            return np.nan
        else:
            return

    def __haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371  # радиус Земли в км
        # переводим в радианы
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def preprocessing(self) -> None:
        # тип БПЛА
        self.data["uav_type"] = self.data["SHR"].str.extract(r"TYP/([^\s)]+)")

        # id полета
        self.data["flight_id"] = self.data["SHR"].str.extract(r"SID/(\d+)")

        # координаты взлета
        self.data["dep_coord"] = self.data["SHR"].str.extract(r"DEP/([0-9]+[NS][0-9]+[EW])")

        # координаты посадки
        self.data["dest_coord"] = self.data["SHR"].str.extract(
            r"DEST/([0-9]+[NS][0-9]+[EW])"
        )

        # плановая дата полета, формат - YYMMDD
        self.data["dof"] = self.data["SHR"].str.extract(r"DOF/(\d{6})")

        # плановое время полета (запись вида ARR - откуда и во сколько,куда и во сколько) формат - HHMM
        times = self.data["ARR"].str.extract(
            r"ARR-[A-Z0-9]+-[A-Z0-9]{4}(?P<dep_hhmm>\d{4})-[A-Z0-9]{4}(?P<arr_hhmm>\d{4})"
        )
        self.data["dep_time_plan"] = times["dep_hhmm"]
        self.data["arr_time_plan"] = times["arr_hhmm"]

        # фактические даты и времени (поиск по DEP/ARR)
        self.data["dep_time_actual"] = None
        self.data["arr_time_actual"] = None
        self.data["dep_date_actual"] = None
        self.data["arr_date_actual"] = None
        atd_series = self.data["DEP"].astype(str).str.extract(r"ATD (\d{4})")[0]
        ata_series = self.data["ARR"].astype(str).str.extract(r"ATA (\d{4})")[0]
        add_series = self.data["DEP"].astype(str).str.extract(r"ADD (\d{6})")[0]
        ada_series = self.data["ARR"].astype(str).str.extract(r"ADA (\d{6})")[0]
        for idx in range(len(self.data)):
            dep_time = atd_series.iloc[idx]
            arr_time = ata_series.iloc[idx]
            dep_date = add_series.iloc[idx]
            arr_date = ada_series.iloc[idx]
            if pd.isna(dep_date):
                dep_date = self.data.loc[idx, "dof"]
            if pd.notna(dep_date):
                self.data.at[idx, "dep_date_actual"] = dep_date
            if pd.notna(dep_time):
                self.data.at[idx, "dep_time_actual"] = dep_time
            if pd.notna(arr_date):
                self.data.at[idx, "arr_date_actual"] = arr_date
            if pd.notna(arr_time):
                self.data.at[idx, "arr_time_actual"] = arr_time
        
        # проходимся по рядам (фактич дата и время или плановые)
        # вылет
        self.data[self.DEP_NAME] = self.data.apply(
            lambda row: self.__combine_date_time(
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
        self.data[self.ARR_NAME] = self.data.apply(
            lambda row: self.__combine_date_time(
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
            self.data[self.DEP_NAME].notna()
            & self.data[self.ARR_NAME].notna()
            & (self.data[self.ARR_NAME] < self.data[self.DEP_NAME])
        )
        self.data.loc[mask, self.ARR_NAME] += pd.Timedelta(days=1)

        # работа с длительностью полета
        self.data["duration_min"] = None
        mask_duration = (
            self.data[self.DEP_NAME].notna() & self.data[self.ARR_NAME].notna()
        )
        self.data.loc[mask_duration, "duration_min"] = (
            self.data.loc[mask_duration, self.ARR_NAME]
            - self.data.loc[mask_duration, self.DEP_NAME]
        ).dt.total_seconds() / 60

        # преобразуем координаты
        # взлет
        self.data[["takeoff_lat", "takeoff_lon"]] = self.data["dep_coord"].apply(
            lambda c: pd.Series(self.__parse_coordinate(c))
        )
        # посадка
        self.data[["landing_lat", "landing_lon"]] = self.data["dest_coord"].apply(
            lambda c: pd.Series(self.__parse_coordinate(c))
        )
        # обаботка координат для таблицы 2025 года (ARR по ключу ADARRZ)
        missing_dest = self.data["landing_lat"].isna() & self.data["ARR"].notna()
        for idx in self.data[missing_dest].index:
            text = str(self.data.at[idx, "ARR"])
            match = re.search(r"ADARRZ ([0-9]+[NS][0-9]+[EW])", text)
            if match:
                lat_val, lon_val = self.__parse_coordinate(match.group(1))
                self.data.at[idx, "landing_lat"] = lat_val
                self.data.at[idx, "landing_lon"] = lon_val
        
        self.data = self.data.drop(
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
        self.data.reset_index(drop=True, inplace=True)

        # Сортирую по дате вылета, чтобы гаранитровать что последний элемент укажет на самую последнюю дату
        self.data = self.data.sort_values(self.DEP_NAME)
        # Добавляю информацию и погоде
        self.__pars_weather()

        # Разделю дату и время
        self.data['dep_date'] = [pd.Timestamp(str(item).split()[0]) for item in self.data[self.DEP_NAME]]
        self.data['dep_time'] = [pd.to_datetime(str(item).split()[1], format='%H:%M:%S').time() if len(str(item).split()) > 1 else np.nan for item in self.data[self.DEP_NAME]]
        self.data['arr_date'] = [pd.Timestamp(str(item).split()[0]) for item in self.data[self.ARR_NAME]]
        self.data['arr_time'] = [pd.to_datetime(str(item).split()[1], format='%H:%M:%S').time() if len(str(item).split()) > 1 else np.nan for item in self.data[self.ARR_NAME]]
        del self.data[self.DEP_NAME]
        del self.data[self.ARR_NAME]

        # Добавляю метку времени года
        self.data["season"] = [self.__get_season(item.month) for item in self.data["arr_date"]]

        # Удалением невалидных записей (не известо время вылета)
        self.data = self.data.loc[:self.data['duration_min'].last_valid_index()]
        print(self.data.info())
        # Интерполяция
        self.data["Т(С)"] = self.data.groupby("season")["Т(С)"].transform(
            lambda x: x.interpolate(method="cubic")
        )
        self.data["f(%)"] = self.data.groupby("season")["f(%)"].transform(
            lambda x: x.interpolate(method="cubic")
        )
        self.data["wind_speed"] = self.data.groupby("season")["wind_speed"].transform(
            lambda x: x.interpolate(method='linear')
        )

        # нужно интерполировать wind_dir, но изначально там хранятся категориальные данные - проблема. Буду преобразовывать и т.д. 
        mapping = {
            "С": 0, "СВ": 45, "В": 90, "ЮВ": 135,
            "Ю": 180, "ЮЗ": 225, "З": 270, "СЗ": 315, "штиль": np.nan
        }
        wind_dir_deg = self.data["wind_dir"].map(mapping).sort_index()
        # перевод в радианы
        wind_dir_rad = np.deg2rad(wind_dir_deg)
        # вектора
        x = np.cos(wind_dir_rad)
        y = np.sin(wind_dir_rad)
        # интерполяция
        x_interp = pd.Series(x).interpolate()
        y_interp = pd.Series(y).interpolate()
        # обратно в угол
        angles = np.arctan2(y_interp, x_interp)
        angles_deg = (np.rad2deg(angles) + 360) % 360
        self.data["wind_dir"] = angles_deg

        # Нормализация типа дронов
        self.data["uav_type"] = self.data["uav_type"].map(self.__normalize_drone_type)

        # Добавлю показатель загруженности области (air_traffic_load)
        traffic_cnt = self.data.groupby('center').count()["season"]
        air_traffic_load = defaultdict(int)
        for idx in traffic_cnt.index:
            air_traffic_load[idx] = traffic_cnt[idx]/self.REGION_AREA_BY_CITY[idx]
        air_traffic_load = pd.DataFrame(list(air_traffic_load.items()), columns=["center", "air_traffic_load"])
        self.data = self.data.merge(air_traffic_load, on="center", how="left")
        
        # Можно добавить и само количество полетов в регионе (traffic_cnt)
        self.data = self.data.merge(traffic_cnt.to_frame(name="traffic_cnt"), left_on="center", right_index=True)

        # Добавлю относительную загружнность по регионам (relative_air_traffic_load)
        self.data["relative_air_traffic_load"] = self.data["traffic_cnt"] / max(self.data["traffic_cnt"])

        # Добавляю пройденную дистанцию и скорость
        self.data["distance"] = [
            self.__haversine(
                self.data.loc[i, "takeoff_lat"],
                self.data.loc[i, "takeoff_lon"],
                self.data.loc[i, "landing_lat"],
                self.data.loc[i, "landing_lon"]
            ) * 1000 for i in range(self.data.shape[0])
        ]
        self.data["speed"] = self.data["distance"].div(self.data["duration_min"].fillna(0))

        print(self.data.info())
        print(self.data.shape)

        self.data.to_excel(self.PREPOC_DATA_PATH + self.PREPOC_DATA_NAME)

# obj = DataLoader()
# obj.preprocessing()