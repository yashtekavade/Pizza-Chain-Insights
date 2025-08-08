-- Database Schema for Pizza Chain Insights
-- This script creates all necessary tables for the pizza chain analytics pipeline

-- Create database (if using MySQL/PostgreSQL)
-- CREATE DATABASE pizza_chain_insights;
-- USE pizza_chain_insights;

-- Table: sku_master
-- Contains product catalog information
CREATE TABLE sku_master (
    sku_id VARCHAR(50) PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_item_name (item_name)
);

-- Table: discounts_applied
-- Contains discount codes and their values
CREATE TABLE discounts_applied (
    discount_code VARCHAR(50) PRIMARY KEY,
    discount_amount DECIMAL(5,2) NOT NULL COMMENT 'Discount percentage (e.g., 10 for 10%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_discount_amount (discount_amount)
);

-- Table: orders
-- Contains order header information
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(75) NOT NULL,
    store_id VARCHAR(10) NOT NULL,
    order_time TIMESTAMP NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_store_id (store_id),
    INDEX idx_order_time (order_time),
    INDEX idx_customer_id (customer_id),
    INDEX idx_total_amount (total_amount)
);

-- Table: order_items
-- Contains individual items within orders
CREATE TABLE order_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    sku_id VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_code VARCHAR(50) DEFAULT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (sku_id) REFERENCES sku_master(sku_id) ON DELETE RESTRICT,
    FOREIGN KEY (discount_code) REFERENCES discounts_applied(discount_code) ON DELETE SET NULL,
    INDEX idx_order_id (order_id),
    INDEX idx_sku_id (sku_id),
    INDEX idx_discount_code (discount_code),
    INDEX idx_quantity (quantity),
    INDEX idx_unit_price (unit_price)
);

-- Table: inventory_logs
-- Contains real-time inventory tracking
CREATE TABLE inventory_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    log_time TIMESTAMP NOT NULL,
    store_id INT NOT NULL,
    sku_id VARCHAR(50) NOT NULL,
    current_stock INT NOT NULL,
    restock_threshold INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku_id) REFERENCES sku_master(sku_id) ON DELETE RESTRICT,
    INDEX idx_log_time (log_time),
    INDEX idx_store_id (store_id),
    INDEX idx_sku_id (sku_id),
    INDEX idx_current_stock (current_stock),
    INDEX idx_restock_threshold (restock_threshold),
    INDEX idx_stock_level (store_id, sku_id, log_time)
);

-- Create a view for low inventory alerts
CREATE VIEW low_inventory_view AS
SELECT 
    il.store_id,
    il.sku_id,
    sm.item_name,
    sm.category,
    il.current_stock,
    il.restock_threshold,
    il.log_time,
    CASE 
        WHEN il.current_stock <= il.restock_threshold THEN 'CRITICAL'
        WHEN il.current_stock <= (il.restock_threshold * 1.2) THEN 'LOW'
        ELSE 'NORMAL'
    END as stock_status
FROM inventory_logs il
JOIN sku_master sm ON il.sku_id = sm.sku_id
WHERE il.log_time = (
    SELECT MAX(log_time) 
    FROM inventory_logs il2 
    WHERE il2.store_id = il.store_id 
    AND il2.sku_id = il.sku_id
);

-- Create a view for order analytics
CREATE VIEW order_analytics_view AS
SELECT 
    o.order_id,
    o.customer_id,
    o.store_id,
    o.order_time,
    DAYOFWEEK(o.order_time) as day_of_week,
    HOUR(o.order_time) as hour_of_day,
    o.total_amount,
    oi.sku_id,
    sm.item_name,
    sm.category,
    oi.quantity,
    oi.unit_price,
    oi.discount_code,
    oi.discount_amount,
    (oi.quantity * oi.unit_price - oi.discount_amount) as item_total
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN sku_master sm ON oi.sku_id = sm.sku_id;

-- Create indexes for performance optimization
CREATE INDEX idx_order_analytics_store_time ON orders(store_id, order_time);
CREATE INDEX idx_order_analytics_category ON sku_master(category);
CREATE INDEX idx_inventory_store_time ON inventory_logs(store_id, log_time);

-- Insert sample discount codes
INSERT INTO discounts_applied (discount_code, discount_amount) VALUES
('WELCOME10', 10.00),
('STUDENT15', 15.00),
('FAMILY20', 20.00),
('WEEKEND25', 25.00),
('LOYALTY30', 30.00),
('BULK35', 35.00);

COMMIT;
