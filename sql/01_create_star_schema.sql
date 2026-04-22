-- PostgreSQL DDL for the analytics star schema

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_region;

CREATE TABLE dim_region (
    region_key INT PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    region_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE dim_customers (
    customer_key INT PRIMARY KEY,
    customer_id INT NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(200) NOT NULL,
    signup_date DATE NOT NULL,
    loyalty_tier VARCHAR(50) NOT NULL,
    region_key INT NOT NULL REFERENCES dim_region(region_key)
);

CREATE TABLE dim_products (
    product_key INT PRIMARY KEY,
    product_id INT NOT NULL UNIQUE,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    unit_cost NUMERIC(12, 2) NOT NULL,
    list_price NUMERIC(12, 2) NOT NULL
);

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter VARCHAR(2) NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INT NOT NULL,
    day INT NOT NULL,
    weekday_name VARCHAR(20) NOT NULL
);

CREATE TABLE fact_sales (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    line_number INT NOT NULL,
    date_key INT NOT NULL REFERENCES dim_date(date_key),
    customer_key INT NOT NULL REFERENCES dim_customers(customer_key),
    product_key INT NOT NULL REFERENCES dim_products(product_key),
    quantity INT NOT NULL,
    returned_qty INT NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    discount_rate NUMERIC(5, 4) NOT NULL,
    gross_revenue NUMERIC(14, 2) NOT NULL,
    discount_amount NUMERIC(14, 2) NOT NULL,
    net_revenue NUMERIC(14, 2) NOT NULL,
    refunded_amount NUMERIC(14, 2) NOT NULL,
    recognized_revenue NUMERIC(14, 2) NOT NULL,
    cogs_amount NUMERIC(14, 2) NOT NULL,
    profit_amount NUMERIC(14, 2) NOT NULL
);

CREATE INDEX idx_fact_sales_date_key ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_customer_key ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product_key ON fact_sales(product_key);
