CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  transaction_uuid UUID UNIQUE NOT NULL, 
  user_id INT NOT NULL,                   
  sku VARCHAR(50) NOT NULL,       --for product        
  quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
  order_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_txn ON orders(transaction_uuid);


CREATE TABLE IF NOT EXISTS inventory_calls (
  id SERIAL PRIMARY KEY,
  order_id INT REFERENCES orders(id) ON DELETE CASCADE,
  transaction_uuid UUID NOT NULL,
  http_status_code INT,
  response_time_ms INT,       
  error_message VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inv_calls_txn ON inventory_calls(transaction_uuid);