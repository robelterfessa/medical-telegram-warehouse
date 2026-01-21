with messages as (

    select
        message_id,
        channel_name,
        message_date,
        message_text,
        message_length,
        view_count,
        forward_count,
        has_image
    from dbt_medical_dbt_medical.stg_telegram_messages

),

channels as (

    select
        channel_key,
        channel_name
    from {{ ref('dim_channels') }}

),

dates as (

    select
        date_key,
        full_date
    from {{ ref('dim_dates') }}

),

joined as (

    select
        m.message_id,
        c.channel_key,
        d.date_key,
        m.message_text,
        m.message_length,
        m.view_count,
        m.forward_count,
        m.has_image
    from messages m
    left join channels c
        on m.channel_name = c.channel_name
    left join dates d
        on m.message_date::date = d.full_date
)

select * from joined
