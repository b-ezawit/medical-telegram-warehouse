with channel_metrics as (
    -- Pre-aggregate performance metrics per channel from staging data
    select
        channel_name,
        min(message_timestamp) as first_post_date,
        max(message_timestamp) as last_post_date,
        count(message_id) as total_posts,
        coalesce(avg(view_count), 0) as avg_views
    from {{ ref('stg_telegram_messages') }}
    group by channel_name
)

select
    -- Generate a unique surrogate key using a cryptographic MD5 hash string
    md5(channel_name) as channel_key,
    channel_name,
    
    -- Classify channel type using wildcard text patterns
    case 
        when lower(channel_name) like '%pharma%' or lower(channel_name) like '%doctor%' then 'Pharmaceutical'
        when lower(channel_name) like '%cosmetic%' or lower(channel_name) like '%beauty%' then 'Cosmetics'
        else 'Medical'
    end as channel_type,
    
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
from channel_metrics