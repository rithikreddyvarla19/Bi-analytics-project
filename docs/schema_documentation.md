# Star Schema Documentation

## Overview

The analytics model is designed as a star schema with one transactional fact table (`fact_sales`) and four descriptive dimensions (`dim_customers`, `dim_products`, `dim_date`, `dim_region`).

Grain of `fact_sales`: one row per order line item (`order_item_id`) for non-cancelled orders.

## Table Definitions

### `fact_sales`
- Primary key: `order_item_id`
- Foreign keys:
  - `date_key` -> `dim_date.date_key`
  - `customer_key` -> `dim_customers.customer_key`
  - `product_key` -> `dim_products.product_key`
- Core measures:
  - `gross_revenue`
  - `discount_amount`
  - `net_revenue`
  - `refunded_amount`
  - `recognized_revenue`
  - `cogs_amount`
  - `profit_amount`

### `dim_customers`
- Primary key: `customer_key`
- Business key: `customer_id`
- Attributes: name, email, signup date, loyalty tier, and regional assignment via `region_key`

### `dim_products`
- Primary key: `product_key`
- Business key: `product_id`
- Attributes: product name, category, subcategory, brand, cost, and list price

### `dim_date`
- Primary key: `date_key` (YYYYMMDD integer)
- Attributes: date, year, quarter, month, month name, week of year, day, weekday

### `dim_region`
- Primary key: `region_key`
- Business key: `region_code`
- Attributes: region name and country

## Relationship Diagram (Text)

- `dim_region (1) -> (many) dim_customers`
- `dim_customers (1) -> (many) fact_sales`
- `dim_products (1) -> (many) fact_sales`
- `dim_date (1) -> (many) fact_sales`

## Modeling Notes

- Returns are incorporated in `fact_sales` through `returned_qty` and `refunded_amount`.
- Recognized revenue is net of discounts and refunds:
  - `recognized_revenue = net_revenue - refunded_amount`
- Profit is calculated as:
  - `profit_amount = recognized_revenue - cogs_amount`
