# Data Dictionary

## Raw Data (`data/raw`)

### `customers_raw.csv`
- `customer_id`: Natural customer identifier
- `first_name`: Customer first name
- `last_name`: Customer last name
- `email`: Customer email (contains intentional nulls in raw layer)
- `signup_date`: Date customer account was created
- `region_code`: Geography code (contains intentional nulls in raw layer)
- `loyalty_tier`: Bronze / Silver / Gold

### `products_raw.csv`
- `product_id`: Natural product identifier
- `product_name`: Product code-like name
- `category`: Top-level category
- `subcategory`: Subcategory
- `brand`: Brand (contains intentional nulls in raw layer)
- `unit_cost`: Unit cost
- `list_price`: Product list price

### `orders_raw.csv`
- `order_id`: Natural order identifier
- `customer_id`: Links to customer
- `order_date`: Order placement date
- `order_status`: Delivered / Cancelled
- `payment_method`: Payment channel

### `order_items_raw.csv`
- `order_item_id`: Natural line-item identifier
- `order_id`: Links to order header
- `line_number`: Sequence within order
- `product_id`: Links to product
- `quantity`: Quantity purchased
- `unit_price`: Unit selling price
- `discount_rate`: Discount as decimal (0.00 to 0.40)
- `unit_cost`: Unit cost used for margin analytics

### `returns_raw.csv`
- `order_item_id`: Returned order line identifier
- `order_id`: Parent order identifier
- `product_id`: Returned product identifier
- `returned_qty`: Quantity returned
- `return_reason`: Return reason text
- `return_date`: Return date

### `regions_raw.csv`
- `region_code`: Region business key
- `region_name`: Human-readable geography
- `country`: Country name

## Processed / Modeled Data (`data/processed`)

### `dim_region.csv`
- `region_key` (PK), `region_code`, `region_name`, `country`

### `dim_customers.csv`
- `customer_key` (PK), `customer_id` (business key), `first_name`, `last_name`, `email`, `signup_date`, `loyalty_tier`, `region_key` (FK)

### `dim_products.csv`
- `product_key` (PK), `product_id` (business key), `product_name`, `category`, `subcategory`, `brand`, `unit_cost`, `list_price`

### `dim_date.csv`
- `date_key` (PK), `date`, `year`, `quarter`, `month`, `month_name`, `week_of_year`, `day`, `weekday_name`

### `fact_sales.csv`
- Keys: `order_item_id` (PK), `order_id`, `line_number`, `date_key`, `customer_key`, `product_key`
- Volumetrics: `quantity`, `returned_qty`
- Pricing: `unit_price`, `discount_rate`
- Financials: `gross_revenue`, `discount_amount`, `net_revenue`, `refunded_amount`, `recognized_revenue`, `cogs_amount`, `profit_amount`
