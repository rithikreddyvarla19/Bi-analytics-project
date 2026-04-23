CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    region TEXT,
    channel_preference TEXT,
    created_at TIMESTAMP,
    is_active BOOLEAN
);

CREATE TABLE IF NOT EXISTS analytics.dim_products (
    product_id TEXT PRIMARY KEY,
    sku TEXT,
    product_name TEXT,
    category TEXT,
    base_price NUMERIC(12,2),
    is_active BOOLEAN
);

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key DATE PRIMARY KEY,
    year INT,
    month INT,
    day INT,
    week_of_year INT
);

CREATE TABLE IF NOT EXISTS analytics.dim_region (
    region_id TEXT PRIMARY KEY,
    region_name TEXT
);

CREATE TABLE IF NOT EXISTS analytics.dim_channel (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT
);

CREATE TABLE IF NOT EXISTS analytics.fact_orders (
    order_id TEXT,
    order_line_id TEXT PRIMARY KEY,
    order_date DATE,
    customer_id TEXT,
    product_id TEXT,
    region TEXT,
    channel TEXT,
    item_quantity INT,
    order_amount NUMERIC(14,2),
    order_status TEXT
);

CREATE TABLE IF NOT EXISTS analytics.fact_payments (
    payment_id TEXT PRIMARY KEY,
    order_id TEXT,
    payment_date DATE,
    payment_method TEXT,
    payment_status TEXT,
    payment_amount NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS analytics.fact_returns (
    return_id TEXT PRIMARY KEY,
    order_id TEXT,
    return_date DATE,
    return_reason TEXT,
    refund_amount NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS analytics.fact_web_events (
    event_id TEXT PRIMARY KEY,
    event_ts TIMESTAMP,
    event_date DATE,
    session_id TEXT,
    customer_id TEXT,
    product_id TEXT,
    event_type TEXT,
    channel TEXT,
    region TEXT
);

CREATE TABLE IF NOT EXISTS analytics.fact_inventory (
    snapshot_date DATE,
    product_id TEXT,
    region TEXT,
    on_hand_qty INT,
    reorder_point INT
);
