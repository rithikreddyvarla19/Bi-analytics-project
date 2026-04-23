SELECT
    snapshot_date,
    region,
    SUM(CASE WHEN on_hand_qty <= 0 THEN 1 ELSE 0 END) AS stockout_products,
    COUNT(DISTINCT product_id) AS tracked_products,
    ROUND(SUM(CASE WHEN on_hand_qty <= 0 THEN 1 ELSE 0 END)::NUMERIC / NULLIF(COUNT(DISTINCT product_id), 0), 4) AS stockout_rate
FROM analytics.fact_inventory
GROUP BY 1,2
ORDER BY 1 DESC, 2;
