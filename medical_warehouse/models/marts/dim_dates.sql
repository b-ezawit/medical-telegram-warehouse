with date_series as (
    -- Extract every unique date present in your clean staging data
    select distinct 
        cast(message_timestamp as date) as full_date
    from {{ ref('stg_telegram_messages') }}
)

select
    -- Generate a clean integer surrogate key (e.g., 20260630)
    cast(to_char(full_date, 'YYYYMMDD') as integer) as date_key,
    full_date,
    
    -- Calendar attributes
    cast(extract(isodow from full_date) as integer) as day_of_week,
    to_char(full_date, 'TMDay') as day_name,
    cast(extract(week from full_date) as integer) as week_of_year,
    cast(extract(month from full_date) as integer) as month,
    to_char(full_date, 'TMMonth') as month_name,
    cast(extract(quarter from full_date) as integer) as quarter,
    cast(extract(year from full_date) as integer) as year,
    
    -- Weekend flag checking if day is Saturday (6) or Sunday (7)
    case 
        when extract(isodow from full_date) in (6, 7) then true 
        else false 
    end as is_weekend
from date_series