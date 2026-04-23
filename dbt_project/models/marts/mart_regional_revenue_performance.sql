select
  region,
  sum(order_amount) as revenue,
  count(distinct order_id) as orders,
  sum(item_quantity) as units
from {{ ref('stg_fact_orders') }}
group by 1
