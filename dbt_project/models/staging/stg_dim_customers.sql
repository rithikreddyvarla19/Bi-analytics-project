select * from {{ source('analytics', 'dim_customers') }}
