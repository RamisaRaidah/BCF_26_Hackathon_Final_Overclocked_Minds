\connect inventory_db;

CREATE TABLE IF NOT EXISTS stock (
  sku VARCHAR(50) PRIMARY KEY,
  available INT NOT NULL DEFAULT 0 CHECK (available >= 0)
);


INSERT INTO stock (sku, available) VALUES
('PS5', 100),
('LAPTOP', 50),
('MOUSE', 200)
ON CONFLICT (sku) DO NOTHING;


CREATE TABLE IF NOT EXISTS adjustments (
  transaction_uuid UUID PRIMARY KEY,
  sku VARCHAR(50) NOT NULL,
  qty INT NOT NULL CHECK (qty > 0),
  applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_adjustments_sku ON adjustments(sku);