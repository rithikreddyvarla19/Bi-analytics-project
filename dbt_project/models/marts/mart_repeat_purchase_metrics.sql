with customer_orders as (
  select customer_id, count(distinct order_id) as order_count
  from {{ ref('stg_fact_orders') }}
  group by 1
)
select
  count(*) as customers,
  sum(case when order_count > 1 then 1 else 0 end) as repeat_customers,
  round(sum(case when order_count > 1 then 1 else 0 end)::numeric / nullif(count(*), 0), 4) as repeat_purchase_rate
from customer_orders
