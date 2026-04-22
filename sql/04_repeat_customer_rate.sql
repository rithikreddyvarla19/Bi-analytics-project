-- Business question: What share of customers are repeat purchasers?

WITH customer_orders AS (
    SELECT
        f.customer_key,
        COUNT(DISTINCT f.order_id) AS order_count
    FROM fact_sales f
    GROUP BY f.customer_key
),
customer_flags AS (
    SELECT
        customer_key,
        order_count,
        CASE WHEN order_count >= 2 THEN 1 ELSE 0 END AS is_repeat_customer
    FROM customer_orders
)
SELECT
    COUNT(*) AS total_customers,
    SUM(is_repeat_customer) AS repeat_customers,
    ROUND(SUM(is_repeat_customer)::NUMERIC / COUNT(*) * 100, 2) AS repeat_customer_rate_pct,
    ROUND(AVG(order_count), 2) AS avg_orders_per_customer
FROM customer_flags;
