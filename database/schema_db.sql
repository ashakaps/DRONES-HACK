-- включить postgis в целевой базе
create extension if not exists postgis;

-- регионы (идентичность и опциональная геометрия)
create table if not exists region (
  id   serial primary key,
  name text not null unique,
  geom geometry(polygon, 4326)
);
create index if not exists idx_region_geom on region using gist (geom);

-- историчные метрики регионов (без удалений: закрываем valid_to и добавляем новую строку)
create table if not exists region_stats (
  id bigserial primary key,
  region_id integer not null references region(id) on delete cascade,
  valid_from date not null,
  valid_to   date,
  traffic_cnt integer not null,
  air_traffic_load numeric not null,
  relative_air_traffic_load numeric not null,
  constraint uq_region_stats unique (region_id, valid_from)
);
create index if not exists idx_region_stats_region on region_stats(region_id, valid_from);

-- типы бпла (справочник)
create table if not exists uav_type (
  id serial primary key,
  code text not null unique,
  description text
);

-- сезоны (опционально; можно не использовать, если выводится из даты)
create table if not exists season_dim (
  code text primary key,
  display_name text not null,
  start_month smallint check (start_month between 1 and 12),
  end_month   smallint check (end_month between 1 and 12)
);

-- факт полёта (узкий состав полей; удобно для индексов и истории загрузок)
create table if not exists flight (
  id bigserial primary key,
  flight_number bigint,
  center_id integer not null references region(id),
  uav_type_id integer not null references uav_type(id),
  dep_timestamp timestamp not null,
  arr_timestamp timestamp,
  source_batch_id text,
  created_at timestamp not null default now(),
  unique (flight_number, dep_timestamp)
);
create index if not exists idx_flight_center on flight(center_id);
create index if not exists idx_flight_uav on flight(uav_type_id);
create index if not exists idx_flight_dep_ts on flight(dep_timestamp);

-- геоточки полёта (1:1; разгружаем ядро и даём gist-индексы)
create table if not exists flight_loc (
  flight_id bigint primary key references flight(id) on delete cascade,
  takeoff_geom geometry(point, 4326),
  landing_geom geometry(point, 4326)
);
create index if not exists idx_flight_loc_takeoff on flight_loc using gist (takeoff_geom);
create index if not exists idx_flight_loc_landing on flight_loc using gist (landing_geom);

-- метрики полёта (1:1; удобно расширять)
create table if not exists flight_metrics (
  flight_id bigint primary key references flight(id) on delete cascade,
  duration_min numeric check (duration_min >= 0),
  distance     numeric check (distance >= 0),
  speed        numeric check (speed >= 0)
);
create index if not exists idx_flight_metrics_duration on flight_metrics(duration_min);

-- погода (1..n на полёт; для одного среза ставьте obs_timestamp = dep_timestamp)
create table if not exists weather_obs (
  id bigserial primary key,
  flight_id bigint not null references flight(id) on delete cascade,
  obs_timestamp timestamp,
  wind_dir   numeric check (wind_dir between 0 and 360),
  wind_speed numeric check (wind_speed >= 0),
  temperature_c numeric,
  humidity_pct  numeric,
  constraint uq_weather_one_per_obs unique (flight_id, obs_timestamp)
);
create index if not exists idx_weather_flight_ts on weather_obs(flight_id, obs_timestamp);

-- связь полёта с сезоном (если используем справочник сезонов)
create table if not exists flight_season (
  flight_id bigint primary key references flight(id) on delete cascade,
  season_code text not null references season_dim(code)
);

-- расширение (jsonb) для дополнительных полей из тз
create table if not exists flight_ext (
  flight_id bigint primary key references flight(id) on delete cascade,
  additional_data jsonb
);
create index if not exists idx_flight_ext_gin on flight_ext using gin (additional_data);