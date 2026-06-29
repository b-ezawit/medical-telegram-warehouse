with source as (
    -- This links to the source file src_telegram.yml
    select * from "medical_db"."raw"."telegram_messages"
),

cleaned as (
    select
        -- 1. Standardizing IDs and Names
        cast(message_id as bigint) as message_id,
        cast(channel_name as varchar(255)) as channel_name,
        
        -- 2. Casting Text Date into an actual timestamp
        cast(message_date as timestamp) as message_timestamp,
        
        -- 3. Handling Text Records
        cast(message_text as text) as message_text,
        
        -- 4. Flags and Paths
        cast(has_media as boolean) as has_media,
        cast(image_path as varchar(500)) as image_path,
        
        -- 5. Standardizing Metrics
        coalesce(cast(views as bigint), 0) as view_count,
        coalesce(cast(forwards as bigint), 0) as forward_count,

        -- 6. Adding Calculated Fields (Calculated at runtime!)
        length(message_text) as message_length,
        case 
            when image_path is not null and image_path != '' then true 
            else false 
        end as has_image_file

    from source
    where 
        -- 7. Filtering out completely invalid records
        message_id is not null
        and message_text is not null 
        and message_text != ''
)

select * from cleaned