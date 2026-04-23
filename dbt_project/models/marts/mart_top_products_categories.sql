select
  p.category,
  p.product_name,
  o.product_id,
  sum(o.order_amount) as revenue,
  sum(o.item_quantity) as units_sold,
  count(distinct o.order_id) as order_count
from {{ ref('stg_fact_orders') }} o
join {{ ref('stg_dim_products') }} p
  on o.product_id = p.product_id
group by 1,2,3
