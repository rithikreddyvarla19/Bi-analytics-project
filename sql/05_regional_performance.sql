-- Business question: Which regions are driving growth and profitability?

WITH regional_monthly AS (
    SELECT
        r.region_name,
        DATE_TRUNC('month', d.date) AS month_start,
        SUM(f.recognized_revenue) AS monthly_revenue,
        SUM(f.profit_amount) AS monthly_profit,
        SUM(f.refunded_amount) AS monthly_refunds
    FROM fact_sales f
    JOIN dim_customers c ON c.customer_key = f.customer_key
    JOIN dim_region r ON r.region_key = c.region_key
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY 1, 2
),
regional_with_growth AS (
    SELECT
        region_name,
        month_start,
        monthly_revenue,
        monthly_profit,
        monthly_refunds,
        LAG(monthly_revenue) OVER (PARTITION BY region_name ORDER BY month_start) AS previous_month_revenue
    FROM regional_monthly
)
SELECT
    region_name,
    month_start,
    ROUND(monthly_revenue, 2) AS monthly_revenue,
    ROUND(monthly_profit, 2) AS monthly_profit,
    ROUND(monthly_refunds, 2) AS monthly_refunds,
    ROUND(
        CASE
            WHEN previous_month_revenue IS NULL OR previous_month_revenue = 0 THEN NULL
            ELSE (monthly_revenue - previous_month_revenue) / previous_month_revenue * 100
        END, 2
    ) AS mom_growth_pct
FROM regional_with_growth
ORDER BY region_name, month_start;
