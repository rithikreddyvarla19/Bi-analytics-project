SELECT
    region,
    SUM(order_amount) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    SUM(item_quantity) AS units,
    ROUND(AVG(order_amount), 2) AS avg_line_revenue
FROM analytics.fact_orders
GROUP BY 1
ORDER BY revenue DESC;
