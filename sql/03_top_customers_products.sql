-- Business question: Who are the top customers and products by revenue?

WITH customer_perf AS (
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        r.region_name,
        SUM(f.recognized_revenue) AS customer_revenue,
        COUNT(DISTINCT f.order_id) AS order_count
    FROM fact_sales f
    JOIN dim_customers c ON c.customer_key = f.customer_key
    JOIN dim_region r ON r.region_key = c.region_key
    GROUP BY 1, 2, 3
),
ranked_customers AS (
    SELECT
        *,
        DENSE_RANK() OVER (ORDER BY customer_revenue DESC) AS customer_rank
    FROM customer_perf
),
product_perf AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        SUM(f.recognized_revenue) AS product_revenue,
        SUM(f.quantity) AS units_sold
    FROM fact_sales f
    JOIN dim_products p ON p.product_key = f.product_key
    GROUP BY 1, 2, 3
),
ranked_products AS (
    SELECT
        *,
        DENSE_RANK() OVER (ORDER BY product_revenue DESC) AS product_rank
    FROM product_perf
)
SELECT
    'CUSTOMER' AS entity_type,
    customer_id::TEXT AS entity_id,
    customer_name AS entity_name,
    region_name AS entity_group,
    ROUND(customer_revenue, 2) AS revenue,
    order_count AS supporting_metric,
    customer_rank AS entity_rank
FROM ranked_customers
WHERE customer_rank <= 10

UNION ALL

SELECT
    'PRODUCT' AS entity_type,
    product_id::TEXT AS entity_id,
    product_name AS entity_name,
    category AS entity_group,
    ROUND(product_revenue, 2) AS revenue,
    units_sold AS supporting_metric,
    product_rank AS entity_rank
FROM ranked_products
WHERE product_rank <= 10

ORDER BY entity_type, entity_rank;
