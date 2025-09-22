import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# put your own months and year
# year = 2023
# months = range(1, 6 + 1)

def parser(year, months, center="Москва"):

    center_id = {
        "Москва": 27612,
        "Санкт-Петербург": 26063,
        "Владивосток": 31960,
        "Екатеринбург": 28440,
        "Казань": 27595,
        "Краснодар": 34927,
        "Нижний Новгород": 27459,
        "Новосибирск": 29634,
        "Ростов-на-Дону": 34730,
        "Самара": 28900,
        "Севастополь": 33994,
        "Сочи": 37099,
    }

    try:
        current_center = center_id[center]
    except:
        current_center = center_id["Москва"]

    def date_extractor(dates_list):
        days = []
        times = []
        merged_datetime = []
        for idx, item in enumerate(dates_list, start=1):
            if idx % 2 == 0:
                days.append(f'{year}.' + item.text)
            else:
                times.append(item.text)
        for idx, day_ in enumerate(days):
            time_ = times[idx]
            string = f"{day_} {time_}"

            datetime_object = datetime.strptime(string, '%Y.%d.%m %H')
            merged_datetime.append(datetime_object)

        return merged_datetime


    def main_table_extractor(table_strings):
        merged_table = []
        for i in table_strings:
            x = i.findAll('td')
            for target_string in x:
                if target_string.text == '':
                    merged_table.append(None)

                else:
                    txt = target_string.text
                    merged_table.append(txt)

        return merged_table


    def build_values_table(cols, values):
        single_table_values = []
        n_iters = int(len(values) / len(cols))
        for i in range(n_iters):
            start_idx = 0 + len(cols) * i
            end_idx = len(cols) + len(cols) * i
            single_table_values.append(values[start_idx:end_idx])

        return single_table_values


    def merge_data_and_table(data, table):
        for string_idx, string in enumerate(table):
            table[string_idx].insert(0, data[string_idx].strftime('%Y.%d.%m %H'))

        return table


    # def build_csv(cols, values):
    #     df = pd.DataFrame(values, columns=[cols])
    #     df.to_csv(f'Weather_{center}_{year}_{"_".join(map(str, months))}.csv', index=False)


    def is_leap_year(year):
        if year % 4 != 0:
            return False
        elif year % 100 != 0:
            return True
        elif year % 400 != 0:
            return False
        else:
            return True


    main_merged_table_values = []

    for target_month_idx in months:
        start_day = 1
        if target_month_idx in [4, 6, 9, 11]:
            end_day = 30
        elif target_month_idx == 2:
            if is_leap_year(year):
                end_day = 29
            else:
                end_day = 28
        else:
            end_day = 31
        weather_url = f'http://www.pogodaiklimat.ru/weather.php?id={current_center}&bday={start_day}&fday={end_day}&amonth={target_month_idx}&ayear={year}&bot=2'
        r = requests.get(weather_url)
        soup = BeautifulSoup(r.content, 'lxml')

        # EXTRACT TIME AND DATE
        day_time = soup.find("div", class_="archive-table-left-column").findAll("td", class_="black")
        all_table_dates = date_extractor(day_time)

        # EXTRACT MAIN TABLE WITH VALUES
        table_strings = soup.select(
            'body > div.background-wrap > main > div > div > div > div > div > div:nth-child(5) > div.big-blue-billet > div > div.archive-table > div.archive-table-wrap > table')

        merged_table = main_table_extractor(table_strings)

        # BUILD FINAL TABLE FOR TARGET MONTH
        col_names = merged_table[:17]  # cut col names
        col_names.insert(0, 'wind_dir')
        col_names[1] = 'wind_speed'
        col_values = merged_table[17:]

        single_table_values = build_values_table(col_names, col_values)
        single_month_table = merge_data_and_table(all_table_dates, single_table_values)
        for row in single_month_table:
            main_merged_table_values.append(row)

    col_names.insert(0, 'date')
    # build_csv(col_names, main_merged_table_values)

    return pd.DataFrame(main_merged_table_values, columns=[col_names])