SELECT
    order_date AS sales_date,
    region,
    channel,
    SUM(order_amount) AS gross_revenue,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(item_quantity) AS units_sold
FROM analytics.fact_orders
GROUP BY 1,2,3
ORDER BY 1 DESC;
