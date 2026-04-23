select * from {{ source('analytics', 'dim_channel') }}
