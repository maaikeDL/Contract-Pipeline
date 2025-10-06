-- Create transactions table
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    product_id VARCHAR(50),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    transaction_date TIMESTAMP,
    payment_method VARCHAR(50)
);

-- Add foreign key
ALTER TABLE transactions 
ADD CONSTRAINT fk_transactions_customer 
FOREIGN KEY (customer_id) REFERENCES customers(customer_id);