with staging as (
    select * from {{ ref('stg_telegram_messages') }}
)

select
    staging.message_id,
    
    -- Foreign Keys matching the surrogate keys in our Dimensions
    md5(staging.channel_name) as channel_key,
    cast(to_char(staging.message_timestamp, 'YYYYMMDD') as integer) as date_key,
    
    -- Metrics and dimensional facts
    staging.message_text,
    staging.message_length,
    staging.view_count,
    staging.forward_count,
    staging.has_image_file as has_image_flag
from staging