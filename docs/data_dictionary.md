# Data Dictionary

## Core entities
- customers: customer profile and acquisition channel preference.
- products: retail catalog and category metadata.
- orders: order line transactions with channel/region coverage.
- payments: payment events and statuses.
- returns: return/refund records linked to orders.
- inventory_snapshots: daily product-region stock levels.
- clickstream_events: website/mobile behavioral events.

## Key identifiers
- `customer_id`, `product_id`, `order_id`, `order_line_id`, `payment_id`, `return_id`, `event_id`, `session_id`.

## Time fields
- `order_ts`, `payment_ts`, `return_ts`, `event_ts`, `snapshot_date`.

## Geographic/channel fields
- `region`, `channel`, `channel_preference`.
