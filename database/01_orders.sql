\connect order_db;

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    transaction_uuid UUID UNIQUE NOT NULL, 
    user_id INT NOT NULL,                  
    product_name VARCHAR(100) NOT NULL,
    quantity INT DEFAULT 1,
    order_status VARCHAR(20) DEFAULT 'PENDING', 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE connection_logs (
    log_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    transaction_uuid UUID,
    http_status_code INT,  
    response_time_ms FLOAT,     
    error_message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);