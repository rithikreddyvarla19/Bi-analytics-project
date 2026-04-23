SELECT
    p.category,
    p.product_name,
    o.product_id,
    SUM(o.order_amount) AS revenue,
    SUM(o.item_quantity) AS units_sold,
    COUNT(DISTINCT o.order_id) AS order_count
FROM analytics.fact_orders o
JOIN analytics.dim_products p ON o.product_id = p.product_id
GROUP BY 1,2,3
ORDER BY revenue DESC;
