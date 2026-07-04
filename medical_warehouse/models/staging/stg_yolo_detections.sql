with source as (
    select * from {{ source('raw_data', 'yolo_detections') }}
),

cleaned as (
    select
        cast(message_id as bigint) as message_id,
        cast(channel_name as varchar(255)) as channel_name,
        cast(detected_class as text) as detected_class,
        cast(confidence_score as numeric) as confidence_score,
        cast(image_category as varchar(50)) as image_category
    from source
    where message_id is not null -- Clean out anomalies or unparsed files
)

select * from cleaned