-- Business question: Which product categories are expanding fastest over time?

WITH category_monthly AS (
    SELECT
        p.category,
        DATE_TRUNC('month', d.date) AS month_start,
        SUM(f.recognized_revenue) AS monthly_revenue
    FROM fact_sales f
    JOIN dim_products p ON p.product_key = f.product_key
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY 1, 2
),
category_growth AS (
    SELECT
        category,
        month_start,
        monthly_revenue,
        LAG(monthly_revenue) OVER (PARTITION BY category ORDER BY month_start) AS prev_revenue
    FROM category_monthly
)
SELECT
    category,
    month_start,
    ROUND(monthly_revenue, 2) AS monthly_revenue,
    ROUND(
        CASE
            WHEN prev_revenue IS NULL OR prev_revenue = 0 THEN NULL
            ELSE (monthly_revenue - prev_revenue) / prev_revenue * 100
        END, 2
    ) AS monthly_growth_pct,
    DENSE_RANK() OVER (PARTITION BY month_start ORDER BY monthly_revenue DESC) AS revenue_rank_in_month
FROM category_growth
ORDER BY month_start, revenue_rank_in_month;
