-- Customer analytics queries

-- Total customers by country
SELECT 
    country,
    COUNT(*) as customer_count
FROM customers 
GROUP BY country
ORDER BY customer_count DESC;

-- Monthly transaction summary
SELECT 
    DATE_TRUNC('month', transaction_date) as month,
    COUNT(*) as total_transactions,
    SUM(total_amount) as total_revenue
FROM transactions 
GROUP BY month
ORDER BY month;