SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(order_amount) AS total_revenue,
    AVG(order_amount) AS avg_order_value,
    SUM(order_amount) AS ltv_proxy
FROM analytics.fact_orders
GROUP BY 1
ORDER BY total_revenue DESC;
