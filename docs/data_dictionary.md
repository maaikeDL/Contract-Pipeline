# Data Dictionary

## Customers Table

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| customer_id | BIGINT | Unique customer identifier |
| first_name | VARCHAR(100) | Customer first name |
| last_name | VARCHAR(100) | Customer last name |
| email | VARCHAR(255) | Customer email address |
| registration_date | TIMESTAMP | Date customer registered |
| country | VARCHAR(100) | Customer country |
| age_group | VARCHAR(10) | Age group category |

## Transactions Table

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| transaction_id | VARCHAR(50) | Unique transaction identifier |
| customer_id | BIGINT | Reference to customer |
| product_id | VARCHAR(50) | Product identifier |
| quantity | INTEGER | Number of items purchased |
| unit_price | DECIMAL(10,2) | Price per unit |
| total_amount | DECIMAL(10,2) | Total transaction amount |
| transaction_date | TIMESTAMP | Date of transaction |
| payment_method | VARCHAR(50) | Payment method used |