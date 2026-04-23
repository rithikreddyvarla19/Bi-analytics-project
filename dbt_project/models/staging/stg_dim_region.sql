select * from {{ source('analytics', 'dim_region') }}
