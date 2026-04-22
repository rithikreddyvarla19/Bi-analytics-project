-- Business question: How well do customer cohorts retain month-over-month?

WITH first_purchase AS (
    SELECT
        f.customer_key,
        MIN(DATE_TRUNC('month', d.date)) AS cohort_month
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY f.customer_key
),
customer_month_activity AS (
    SELECT DISTINCT
        f.customer_key,
        DATE_TRUNC('month', d.date) AS activity_month
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
),
cohort_activity AS (
    SELECT
        fp.cohort_month,
        cma.activity_month,
        (DATE_PART('year', cma.activity_month) - DATE_PART('year', fp.cohort_month)) * 12
        + (DATE_PART('month', cma.activity_month) - DATE_PART('month', fp.cohort_month)) AS month_number,
        COUNT(DISTINCT cma.customer_key) AS active_customers
    FROM first_purchase fp
    JOIN customer_month_activity cma ON cma.customer_key = fp.customer_key
    GROUP BY 1, 2, 3
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_key) AS cohort_size
    FROM first_purchase
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    ca.activity_month,
    ca.month_number,
    cs.cohort_size,
    ca.active_customers,
    ROUND(ca.active_customers::NUMERIC / cs.cohort_size * 100, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_sizes cs ON cs.cohort_month = ca.cohort_month
WHERE ca.month_number BETWEEN 0 AND 12
ORDER BY ca.cohort_month, ca.month_number;
