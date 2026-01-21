with dates as (

    select
        generate_series(
            (select min(message_date)::date from dbt_medical_dbt_medical.stg_telegram_messages),
            (select max(message_date)::date from dbt_medical_dbt_medical.stg_telegram_messages),
            interval '1 day'
        )::date as full_date

)

select
    to_char(full_date, 'YYYYMMDD')::integer as date_key,
    full_date,
    extract(isodow from full_date)::integer as day_of_week,
    to_char(full_date, 'Day') as day_name,
    extract(week from full_date)::integer as week_of_year,
    extract(month from full_date)::integer as month,
    to_char(full_date, 'Month') as month_name,
    extract(quarter from full_date)::integer as quarter,
    extract(year from full_date)::integer as year,
    case when extract(isodow from full_date) in (6, 7) then true else false end as is_weekend
from dates
