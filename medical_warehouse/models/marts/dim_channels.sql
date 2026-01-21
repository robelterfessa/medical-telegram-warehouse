with base as (

    select
        channel_name,
        min(message_date)::date as first_post_date,
        max(message_date)::date as last_post_date,
        count(*) as total_posts,
        avg(view_count)::numeric as avg_views
    from dbt_medical_dbt_medical.stg_telegram_messages
    group by channel_name

)

select
    row_number() over (order by channel_name) as channel_key,
    channel_name,
    'Unknown'::text as channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
from base
