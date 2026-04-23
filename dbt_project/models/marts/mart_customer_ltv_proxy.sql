select
  customer_id,
  count(distinct order_id) as total_orders,
  sum(order_amount) as total_revenue,
  sum(order_amount) as ltv_proxy
from {{ ref('stg_fact_orders') }}
group by 1
