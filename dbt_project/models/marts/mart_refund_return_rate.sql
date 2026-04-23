select
  count(distinct o.order_id) as total_orders,
  count(distinct r.order_id) as returned_orders,
  round(count(distinct r.order_id)::numeric / nullif(count(distinct o.order_id), 0), 4) as return_rate
from {{ ref('stg_fact_orders') }} o
left join {{ ref('stg_fact_returns') }} r
  on o.order_id = r.order_id
