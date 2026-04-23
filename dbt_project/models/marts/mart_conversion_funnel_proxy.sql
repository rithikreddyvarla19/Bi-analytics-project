select
  event_date,
  channel,
  sum(case when event_type = 'page_view' then 1 else 0 end) as page_views,
  sum(case when event_type = 'product_view' then 1 else 0 end) as product_views,
  sum(case when event_type = 'add_to_cart' then 1 else 0 end) as add_to_cart,
  sum(case when event_type = 'checkout_start' then 1 else 0 end) as checkout_start,
  sum(case when event_type = 'purchase' then 1 else 0 end) as purchases
from {{ ref('stg_fact_web_events') }}
group by 1,2
