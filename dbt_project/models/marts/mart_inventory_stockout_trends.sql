select
  snapshot_date,
  region,
  sum(case when on_hand_qty <= 0 then 1 else 0 end) as stockout_products,
  count(distinct product_id) as tracked_products,
  round(sum(case when on_hand_qty <= 0 then 1 else 0 end)::numeric / nullif(count(distinct product_id), 0), 4) as stockout_rate
from {{ source('analytics', 'fact_inventory') }}
group by 1,2
