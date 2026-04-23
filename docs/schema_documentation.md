# Schema Documentation

## Gold dimensions
- `dim_customers(customer_id, first_name, last_name, email, region, channel_preference, created_at, is_active)`
- `dim_products(product_id, sku, product_name, category, base_price, is_active)`
- `dim_date(date_key, year, month, day, week_of_year)`
- `dim_region(region_id, region_name)`
- `dim_channel(channel_id, channel_name)`

## Gold facts
- `fact_orders(order_id, order_line_id, order_date, customer_id, product_id, region, channel, item_quantity, order_amount, order_status)`
- `fact_payments(payment_id, order_id, payment_date, payment_method, payment_status, payment_amount)`
- `fact_returns(return_id, order_id, return_date, return_reason, refund_amount)`
- `fact_web_events(event_id, event_ts, event_date, session_id, customer_id, product_id, event_type, channel, region)`
- `fact_inventory(snapshot_date, product_id, region, on_hand_qty, reorder_point)`

## Aggregate gold marts
- `daily_sales`
- `conversion_funnel_proxy`
- `inventory_stockout_trends`
- `streaming_hourly_activity`
- `streaming_product_activity`
