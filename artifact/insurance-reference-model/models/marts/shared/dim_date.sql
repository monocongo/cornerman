-- Grain: one row per calendar day, 2023-01-01 through 2026-12-31.
with spine as (
    select unnest(generate_series(
        date '2023-01-01', date '2026-12-31', interval 1 day
    )) as date_day
)

select
    date_day::date as date_day,
    extract(year from date_day)::integer as year_number,
    extract(quarter from date_day)::integer as quarter_number,
    extract(month from date_day)::integer as month_number,
    strftime(date_day, '%B') as month_name,
    extract(day from date_day)::integer as day_of_month,
    extract(dow from date_day)::integer as day_of_week_number,
    strftime(date_day, '%A') as day_name,
    (extract(dow from date_day) in (0, 6)) as is_weekend
from spine
