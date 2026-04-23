SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT r.order_id) AS returned_orders,
    ROUND(COUNT(DISTINCT r.order_id)::NUMERIC / NULLIF(COUNT(DISTINCT o.order_id), 0), 4) AS return_rate
FROM analytics.fact_orders o
LEFT JOIN analytics.fact_returns r ON o.order_id = r.order_id;
