from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import get_db
from . import schemas

app = FastAPI(title="Medical Telegram Warehouse API")


@app.get("/api/reports/top-products", response_model=List[schemas.ProductReport])
def top_products(limit: int = Query(10, gt=0, le=100), db: Session = Depends(get_db)):
    """
    Returns the most frequently mentioned words in message_text across all channels.
    Very simple token-based approach for demo purposes.
    """
    sql = text("""
        with tokens as (
            select
                lower(unnest(string_to_array(regexp_replace(message_text, '[^a-zA-Z0-9 ]', ' ', 'g'), ' '))) as term
            from dbt_medical_dbt_medical.fct_messages
        )
        select term, count(*) as count
        from tokens
        where term <> ''
        group by term
        order by count desc
        limit :limit
    """)
    rows = db.execute(sql, {"limit": limit}).fetchall()
    return [schemas.ProductReport(term=r.term, count=r.count) for r in rows]


@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """
    Returns daily posting activity and total views for a specific channel.
    """
    sql = text("""
        select
            d.full_date::text as date,
            count(f.message_id) as message_count,
            coalesce(sum(f.view_count), 0) as total_views
        from dbt_medical_dbt_medical.fct_messages f
        join dbt_medical_dbt_medical.dim_channels c
          on f.channel_key = c.channel_key
        join dbt_medical_dbt_medical.dim_dates d
          on f.date_key = d.date_key
        where lower(c.channel_name) = lower(:channel_name)
        group by d.full_date
        order by d.full_date
    """)
    rows = db.execute(sql, {"channel_name": channel_name}).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Channel not found or no data")
    return [schemas.ChannelActivity(date=r.date, message_count=r.message_count, total_views=r.total_views) for r in rows]


@app.get("/api/search/messages", response_model=List[schemas.MessageItem])
def search_messages(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, gt=0, le=100),
    db: Session = Depends(get_db),
):
    """
    Searches for messages containing a specific keyword.
    """
    sql = text("""
        select
            f.message_id,
            c.channel_name,
            to_char(d.full_date, 'YYYY-MM-DD') as message_date,
            f.message_text,
            f.view_count,
            f.forward_count,
            f.has_image
        from dbt_medical_dbt_medical.fct_messages f
        join dbt_medical_dbt_medical.dim_channels c
          on f.channel_key = c.channel_key
        join dbt_medical_dbt_medical.dim_dates d
          on f.date_key = d.date_key
        where f.message_text ilike '%' || :q || '%'
        order by d.full_date desc
        limit :limit
    """)
    rows = db.execute(sql, {"q": query, "limit": limit}).fetchall()
    return [
        schemas.MessageItem(
            message_id=r.message_id,
            channel_name=r.channel_name,
            message_date=r.message_date,
            message_text=r.message_text,
            view_count=r.view_count,
            forward_count=r.forward_count,
            has_image=r.has_image,
        )
        for r in rows
    ]


@app.get("/api/reports/visual-content", response_model=List[schemas.VisualContentStats])
def visual_content_stats(db: Session = Depends(get_db)):
    """
    Returns statistics about image usage and image categories across channels.
    """
    sql = text("""
        with msg as (
            select
                c.channel_name,
                f.message_id,
                f.has_image
            from dbt_medical_dbt_medical.fct_messages f
            join dbt_medical_dbt_medical.dim_channels c
              on f.channel_key = c.channel_key
        ),
        cat as (
            select
                m.channel_name,
                m.message_id,
                coalesce(i.image_category, 'other') as image_category
            from msg m
            left join dbt_medical_dbt_medical.fct_image_detections i
              on m.message_id = i.message_id
        )
        select
            channel_name,
            count(*) as total_messages,
            count(*) filter (where has_image) as messages_with_images,
            count(*) filter (where image_category = 'promotional') as promotional,
            count(*) filter (where image_category = 'product_display') as product_display,
            count(*) filter (where image_category = 'lifestyle') as lifestyle,
            count(*) filter (where image_category = 'other') as other
        from msg
        left join dbt_medical_dbt_medical.fct_image_detections i
          on msg.message_id = i.message_id
        group by channel_name
        order by channel_name
    """)
    rows = db.execute(sql).fetchall()
    return [
        schemas.VisualContentStats(
            channel_name=r.channel_name,
            total_messages=r.total_messages,
            messages_with_images=r.messages_with_images,
            promotional=r.promotional,
            product_display=r.product_display,
            lifestyle=r.lifestyle,
            other=r.other,
        )
        for r in rows
    ]
