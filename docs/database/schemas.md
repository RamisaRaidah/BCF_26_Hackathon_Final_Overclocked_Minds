# Database Schema

This document describes the core database tables used in the hackathon project.  
The schema focuses on order processing, inventory validation, and stock adjustment tracking.

---

## 1. orders

Stores all customer orders and their current processing status.

### Columns

| COLUMN_NAME        | DATA_TYPE      | NULLABLE | DATA_DEFAULT            | CONSTRAINTS                          | COMMENTS |
|--------------------|---------------|----------|--------------------------|--------------------------------------|----------|
| id                 | SERIAL        | No       | auto-increment           | PRIMARY KEY                          | Internal order identifier. |
| transaction_uuid   | UUID          | No       | null                     | UNIQUE                               | Global transaction identifier used across services. |
| user_id            | INT           | No       | null                     | —                                    | ID of the user who placed the order. |
| sku                | VARCHAR(50)   | No       | null                     | —                                    | Product SKU being ordered. |
| quantity           | INT           | No       | 1                        | CHECK (quantity > 0)                 | Number of units ordered. |
| order_status       | VARCHAR(20)   | No       | 'PENDING'                | —                                    | Current status of the order (PENDING, CONFIRMED, FAILED, etc.). |
| created_at         | TIMESTAMP     | No       | CURRENT_TIMESTAMP        | —                                    | Order creation timestamp. |
| updated_at         | TIMESTAMP     | No       | CURRENT_TIMESTAMP        | —                                    | Last update timestamp. |

### Indexes
- `idx_orders_txn` on (`transaction_uuid`)

### Purpose
Represents the **source of truth for orders** in the system.  
Each order is uniquely identified using a `transaction_uuid` to support distributed workflows and idempotent processing.

---

## 2. inventory_calls

Logs all calls made to the inventory service for a specific order.

### Columns

| COLUMN_NAME        | DATA_TYPE     | NULLABLE | DATA_DEFAULT     | CONSTRAINTS                                   | COMMENTS |
|--------------------|--------------|----------|------------------|-----------------------------------------------|----------|
| id                 | SERIAL       | No       | auto-increment   | PRIMARY KEY                                   | Internal log identifier. |
| order_id           | INT          | Yes      | null             | FOREIGN KEY → orders(id) ON DELETE CASCADE    | Related order ID. |
| transaction_uuid   | UUID         | No       | null             | —                                             | Transaction identifier for traceability. |
| http_status_code   | INT          | Yes      | null             | —                                             | HTTP response status from inventory service. |
| response_time_ms   | INT          | Yes      | null             | —                                             | Time taken for the inventory call (ms). |
| error_message      | VARCHAR(255) | Yes      | null             | —                                             | Error message if the call failed. |
| created_at         | TIMESTAMP    | No       | CURRENT_TIMESTAMP| —                                             | Log creation timestamp. |

### Indexes
- `idx_inv_calls_txn` on (`transaction_uuid`)

### Purpose
Provides **observability and debugging support** by tracking every inventory service interaction.  
Useful for latency analysis, failure tracing, and audit logs during order processing.

---

## 3. stock

Maintains the available quantity for each product SKU.

### Columns

| COLUMN_NAME | DATA_TYPE    | NULLABLE | DATA_DEFAULT | CONSTRAINTS                     | COMMENTS |
|------------|-------------|----------|--------------|----------------------------------|----------|
| sku        | VARCHAR(50) | No       | null         | PRIMARY KEY                      | Unique product identifier. |
| available  | INT         | No       | 0            | CHECK (available >= 0)           | Current available stock count. |

### Purpose
Acts as the **central inventory store** for products.  
Ensures stock levels never go negative and supports availability checks before order confirmation.

---

## 4. adjustments

Records successful stock deductions tied to a transaction.

### Columns

| COLUMN_NAME        | DATA_TYPE    | NULLABLE | DATA_DEFAULT       | CONSTRAINTS            | COMMENTS |
|--------------------|-------------|----------|--------------------|------------------------|----------|
| transaction_uuid   | UUID        | No       | null               | PRIMARY KEY            | Transaction that caused the adjustment. |
| sku                | VARCHAR(50) | No       | null               | —                      | Product SKU adjusted. |
| qty                | INT         | No       | null               | CHECK (qty > 0)        | Quantity deducted from stock. |
| applied_at         | TIMESTAMP   | No       | CURRENT_TIMESTAMP  | —                      | Time when the adjustment was applied. |

### Indexes
- `idx_adjustments_sku` on (`sku`)

### Purpose
Ensures **idempotent inventory updates** by recording applied adjustments per transaction.  
Prevents duplicate stock deductions during retries or partial failures.

---

## Overall Design Notes

- `transaction_uuid` is used as a **cross-service correlation key**
- Inventory calls are logged separately for **traceability**
- Stock updates are protected using the `adjustments` table to ensure **exactly-once semantics**
- Foreign key cascading ensures cleanup of logs when orders are deleted

