with source as (

    select
        message_id,
        channel_name,
        message_date::timestamptz as message_date,
        message_text,
        has_media,
        image_path,
        views::integer as views,
        forwards::integer as forwards
    from raw.telegram_messages

)

select
    message_id,
    lower(channel_name) as channel_name,
    message_date,
    message_text,
    length(coalesce(message_text, '')) as message_length,
    coalesce(has_media, false) as has_image,
    image_path,
    coalesce(views, 0) as view_count,
    coalesce(forwards, 0) as forward_count
from source
where message_text is not null
