select * from {{ source('analytics', 'fact_returns') }}
