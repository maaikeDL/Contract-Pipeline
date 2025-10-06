-- Create customers table
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    registration_date TIMESTAMP,
    country VARCHAR(100),
    age_group VARCHAR(10)
);