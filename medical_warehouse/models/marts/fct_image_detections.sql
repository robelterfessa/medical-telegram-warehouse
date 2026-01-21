with detections as (

    select
        message_id,
        lower(channel_name) as channel_name,
        detected_class,
        confidence_score
    from raw.image_detections

),

messages as (

    select
        message_id,
        channel_key,
        date_key,
        has_image,
        view_count,
        forward_count
    from dbt_medical_dbt_medical.fct_messages

),

joined as (

    select
        m.message_id,
        m.channel_key,
        m.date_key,
        d.detected_class,
        d.confidence_score,
        case
            when m.has_image = false then 'other'
            when d.detected_class ilike '%person%' and d.detected_class ilike '%bottle%' then 'promotional'
            when d.detected_class ilike '%person%' then 'lifestyle'
            when d.detected_class ilike '%bottle%' or d.detected_class ilike '%cup%' or d.detected_class ilike '%container%' then 'product_display'
            else 'other'
        end as image_category
    from messages m
    left join detections d
      on m.message_id = d.message_id
)

select * from joined
