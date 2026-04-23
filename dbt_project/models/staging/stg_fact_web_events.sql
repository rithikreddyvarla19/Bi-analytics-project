select * from {{ source('analytics', 'fact_web_events') }}
