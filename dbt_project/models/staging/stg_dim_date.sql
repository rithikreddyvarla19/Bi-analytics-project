select * from {{ source('analytics', 'dim_date') }}
