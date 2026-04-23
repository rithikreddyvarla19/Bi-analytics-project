select * from {{ source('analytics', 'dim_products') }}
