select
  order_date as sales_date,
  region,
  channel,
  sum(order_amount) as gross_sales,
  count(distinct order_id) as orders,
  sum(item_quantity) as units_sold
from {{ ref('stg_fact_orders') }}
group by 1,2,3
