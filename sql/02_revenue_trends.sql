-- Business question: How are revenue and profitability trending monthly?

WITH monthly_revenue AS (
    SELECT
        d.year,
        d.month,
        DATE_TRUNC('month', d.date) AS month_start,
        SUM(f.recognized_revenue) AS total_revenue,
        SUM(f.profit_amount) AS total_profit,
        SUM(f.quantity) AS units_sold
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY 1, 2, 3
),
monthly_with_growth AS (
    SELECT
        month_start,
        total_revenue,
        total_profit,
        units_sold,
        LAG(total_revenue) OVER (ORDER BY month_start) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    month_start,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(total_profit, 2) AS total_profit,
    units_sold,
    ROUND(
        CASE
            WHEN previous_month_revenue IS NULL OR previous_month_revenue = 0 THEN NULL
            ELSE (total_revenue - previous_month_revenue) / previous_month_revenue * 100
        END, 2
    ) AS revenue_growth_pct
FROM monthly_with_growth
ORDER BY month_start;
