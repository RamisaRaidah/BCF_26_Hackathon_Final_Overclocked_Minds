\connect inventory_db;

CREATE TABLE products (
    product_name VARCHAR(100) PRIMARY KEY, 
    stock_count INT DEFAULT 0
);


INSERT INTO products (product_name, stock_count) VALUES 
('PS5', 100),
('Laptop', 50),
('Mouse', 200);

CREATE TABLE processed_transactions (
    transaction_uuid UUID PRIMARY KEY,
    product_name VARCHAR(100),
    quantity_deducted INT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);