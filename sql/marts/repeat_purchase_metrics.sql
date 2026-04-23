WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM analytics.fact_orders
    GROUP BY 1
)
SELECT
    COUNT(*) AS customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*), 4) AS repeat_purchase_rate
FROM customer_orders;
