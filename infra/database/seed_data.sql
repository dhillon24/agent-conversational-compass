-- Seed data for Customer Service Database
-- This script populates the database with realistic synthetic data

-- Insert product categories
INSERT INTO product_categories (id, name, description) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'Electronics', 'Electronic devices and accessories'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Clothing', 'Apparel and fashion items'),
    ('550e8400-e29b-41d4-a716-446655440003', 'Home & Garden', 'Home improvement and garden supplies'),
    ('550e8400-e29b-41d4-a716-446655440004', 'Books', 'Books and educational materials'),
    ('550e8400-e29b-41d4-a716-446655440005', 'Sports & Outdoors', 'Sports equipment and outdoor gear');

-- Insert products
INSERT INTO products (id, sku, name, description, category_id, price, cost, weight, stock_quantity) VALUES
    ('650e8400-e29b-41d4-a716-446655440001', 'ELEC-001', 'Wireless Bluetooth Headphones', 'Premium noise-canceling wireless headphones', '550e8400-e29b-41d4-a716-446655440001', 199.99, 89.99, 0.5, 150),
    ('650e8400-e29b-41d4-a716-446655440002', 'ELEC-002', 'Smartphone Case', 'Protective case for smartphones', '550e8400-e29b-41d4-a716-446655440001', 29.99, 12.99, 0.1, 500),
    ('650e8400-e29b-41d4-a716-446655440003', 'CLOTH-001', 'Cotton T-Shirt', 'Comfortable 100% cotton t-shirt', '550e8400-e29b-41d4-a716-446655440002', 24.99, 8.99, 0.3, 200),
    ('650e8400-e29b-41d4-a716-446655440004', 'CLOTH-002', 'Denim Jeans', 'Classic blue denim jeans', '550e8400-e29b-41d4-a716-446655440002', 79.99, 35.99, 0.8, 100),
    ('650e8400-e29b-41d4-a716-446655440005', 'HOME-001', 'Coffee Maker', 'Programmable drip coffee maker', '550e8400-e29b-41d4-a716-446655440003', 89.99, 45.99, 3.2, 75),
    ('650e8400-e29b-41d4-a716-446655440006', 'BOOK-001', 'Programming Guide', 'Complete guide to modern programming', '550e8400-e29b-41d4-a716-446655440004', 49.99, 20.99, 1.1, 300),
    ('650e8400-e29b-41d4-a716-446655440007', 'SPORT-001', 'Running Shoes', 'Professional running shoes', '550e8400-e29b-41d4-a716-446655440005', 129.99, 65.99, 1.2, 80),
    ('650e8400-e29b-41d4-a716-446655440008', 'ELEC-003', 'Laptop Stand', 'Adjustable aluminum laptop stand', '550e8400-e29b-41d4-a716-446655440001', 59.99, 25.99, 1.5, 120);

-- Insert customers
INSERT INTO customers (id, email, first_name, last_name, phone, status) VALUES
    ('750e8400-e29b-41d4-a716-446655440001', 'john.doe@email.com', 'John', 'Doe', '+1-555-0101', 'active'),
    ('750e8400-e29b-41d4-a716-446655440002', 'jane.smith@email.com', 'Jane', 'Smith', '+1-555-0102', 'active'),
    ('750e8400-e29b-41d4-a716-446655440003', 'mike.johnson@email.com', 'Mike', 'Johnson', '+1-555-0103', 'active'),
    ('750e8400-e29b-41d4-a716-446655440004', 'sarah.wilson@email.com', 'Sarah', 'Wilson', '+1-555-0104', 'active'),
    ('750e8400-e29b-41d4-a716-446655440005', 'test_user@email.com', 'Test', 'User', '+1-555-0105', 'active'),
    ('750e8400-e29b-41d4-a716-446655440006', 'alex.brown@email.com', 'Alex', 'Brown', '+1-555-0106', 'active'),
    ('750e8400-e29b-41d4-a716-446655440007', 'lisa.davis@email.com', 'Lisa', 'Davis', '+1-555-0107', 'active');

-- Insert customer addresses
INSERT INTO customer_addresses (customer_id, type, street_address, city, state, postal_code, is_default) VALUES
    ('750e8400-e29b-41d4-a716-446655440001', 'shipping', '123 Main St', 'New York', 'NY', '10001', true),
    ('750e8400-e29b-41d4-a716-446655440001', 'billing', '123 Main St', 'New York', 'NY', '10001', true),
    ('750e8400-e29b-41d4-a716-446655440002', 'shipping', '456 Oak Ave', 'Los Angeles', 'CA', '90210', true),
    ('750e8400-e29b-41d4-a716-446655440002', 'billing', '456 Oak Ave', 'Los Angeles', 'CA', '90210', true),
    ('750e8400-e29b-41d4-a716-446655440003', 'shipping', '789 Pine Rd', 'Chicago', 'IL', '60601', true),
    ('750e8400-e29b-41d4-a716-446655440005', 'shipping', '321 Test Blvd', 'San Francisco', 'CA', '94102', true);

-- Insert orders with specific order numbers including #123
INSERT INTO orders (id, order_number, customer_id, status, subtotal, tax_amount, shipping_amount, total_amount, payment_status, shipping_address, billing_address, created_at, shipped_at) VALUES
    ('850e8400-e29b-41d4-a716-446655440001', '123', '750e8400-e29b-41d4-a716-446655440005', 'shipped', 229.98, 18.40, 9.99, 258.37, 'paid', 
     '{"street": "321 Test Blvd", "city": "San Francisco", "state": "CA", "postal_code": "94102"}',
     '{"street": "321 Test Blvd", "city": "San Francisco", "state": "CA", "postal_code": "94102"}',
     '2024-01-15 10:30:00+00', '2024-01-16 14:20:00+00'),
    
    ('850e8400-e29b-41d4-a716-446655440002', '12345', '750e8400-e29b-41d4-a716-446655440001', 'delivered', 199.99, 16.00, 9.99, 225.98, 'paid',
     '{"street": "123 Main St", "city": "New York", "state": "NY", "postal_code": "10001"}',
     '{"street": "123 Main St", "city": "New York", "state": "NY", "postal_code": "10001"}',
     '2024-01-10 09:15:00+00', '2024-01-11 16:45:00+00'),
     
    ('850e8400-e29b-41d4-a716-446655440003', '67890', '750e8400-e29b-41d4-a716-446655440002', 'processing', 104.98, 8.40, 9.99, 123.37, 'paid',
     '{"street": "456 Oak Ave", "city": "Los Angeles", "state": "CA", "postal_code": "90210"}',
     '{"street": "456 Oak Ave", "city": "Los Angeles", "state": "CA", "postal_code": "90210"}',
     '2024-01-20 14:22:00+00', NULL),
     
    ('850e8400-e29b-41d4-a716-446655440004', '11111', '750e8400-e29b-41d4-a716-446655440003', 'delivered', 89.99, 7.20, 9.99, 107.18, 'paid',
     '{"street": "789 Pine Rd", "city": "Chicago", "state": "IL", "postal_code": "60601"}',
     '{"street": "789 Pine Rd", "city": "Chicago", "state": "IL", "postal_code": "60601"}',
     '2024-01-05 11:30:00+00', '2024-01-06 13:15:00+00'),
     
    ('850e8400-e29b-41d4-a716-446655440005', '22222', '750e8400-e29b-41d4-a716-446655440004', 'cancelled', 79.99, 6.40, 9.99, 96.38, 'refunded',
     '{"street": "555 Elm St", "city": "Miami", "state": "FL", "postal_code": "33101"}',
     '{"street": "555 Elm St", "city": "Miami", "state": "FL", "postal_code": "33101"}',
     '2024-01-18 16:45:00+00', NULL);

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
    -- Order #123 (Test User's order)
    ('850e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440001', 1, 199.99, 199.99), -- Wireless Headphones
    ('850e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440002', 1, 29.99, 29.99),   -- Smartphone Case
    
    -- Order #12345 (John Doe's order)
    ('850e8400-e29b-41d4-a716-446655440002', '650e8400-e29b-41d4-a716-446655440001', 1, 199.99, 199.99), -- Wireless Headphones
    
    -- Order #67890 (Jane Smith's order)
    ('850e8400-e29b-41d4-a716-446655440003', '650e8400-e29b-41d4-a716-446655440003', 2, 24.99, 49.98),   -- 2x Cotton T-Shirts
    ('850e8400-e29b-41d4-a716-446655440003', '650e8400-e29b-41d4-a716-446655440006', 1, 49.99, 49.99),   -- Programming Guide
    ('850e8400-e29b-41d4-a716-446655440003', '650e8400-e29b-41d4-a716-446655440008', 1, 59.99, 59.99),   -- Laptop Stand
    
    -- Order #11111 (Mike Johnson's order)
    ('850e8400-e29b-41d4-a716-446655440004', '650e8400-e29b-41d4-a716-446655440005', 1, 89.99, 89.99),   -- Coffee Maker
    
    -- Order #22222 (Sarah Wilson's cancelled order)
    ('850e8400-e29b-41d4-a716-446655440005', '650e8400-e29b-41d4-a716-446655440004', 1, 79.99, 79.99);   -- Denim Jeans

-- Insert shipments
INSERT INTO shipments (order_id, tracking_number, carrier, status, shipped_at, estimated_delivery, delivered_at) VALUES
    ('850e8400-e29b-41d4-a716-446655440001', 'TRK123456789', 'FedEx', 'in_transit', '2024-01-16 14:20:00+00', '2024-01-18 17:00:00+00', NULL),
    ('850e8400-e29b-41d4-a716-446655440002', 'TRK987654321', 'UPS', 'delivered', '2024-01-11 16:45:00+00', '2024-01-13 17:00:00+00', '2024-01-13 15:30:00+00'),
    ('850e8400-e29b-41d4-a716-446655440004', 'TRK555666777', 'USPS', 'delivered', '2024-01-06 13:15:00+00', '2024-01-08 17:00:00+00', '2024-01-08 14:22:00+00');

-- Insert payment transactions
INSERT INTO payment_transactions (order_id, transaction_id, payment_method, amount, status, processed_at) VALUES
    ('850e8400-e29b-41d4-a716-446655440001', 'TXN_123_001', 'credit_card', 258.37, 'completed', '2024-01-15 10:32:00+00'),
    ('850e8400-e29b-41d4-a716-446655440002', 'TXN_12345_001', 'credit_card', 225.98, 'completed', '2024-01-10 09:17:00+00'),
    ('850e8400-e29b-41d4-a716-446655440003', 'TXN_67890_001', 'paypal', 123.37, 'completed', '2024-01-20 14:24:00+00'),
    ('850e8400-e29b-41d4-a716-446655440004', 'TXN_11111_001', 'credit_card', 107.18, 'completed', '2024-01-05 11:32:00+00'),
    ('850e8400-e29b-41d4-a716-446655440005', 'TXN_22222_001', 'credit_card', 96.38, 'refunded', '2024-01-18 16:47:00+00');

-- Insert support tickets
INSERT INTO support_tickets (ticket_number, customer_id, order_id, subject, description, status, priority, category) VALUES
    ('TICK-001', '750e8400-e29b-41d4-a716-446655440005', '850e8400-e29b-41d4-a716-446655440001', 'Order Status Inquiry', 'Customer asking about shipping status of order #123', 'open', 'medium', 'shipping'),
    ('TICK-002', '750e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440002', 'Product Quality Issue', 'Headphones have connectivity issues', 'in_progress', 'high', 'product_quality'),
    ('TICK-003', '750e8400-e29b-41d4-a716-446655440004', '850e8400-e29b-41d4-a716-446655440005', 'Refund Request', 'Customer wants to cancel order and get refund', 'resolved', 'medium', 'refund');

-- Insert refunds
INSERT INTO refunds (order_id, payment_transaction_id, refund_number, amount, reason, status, processed_by, processed_at) VALUES
    ('850e8400-e29b-41d4-a716-446655440005', 
     (SELECT id FROM payment_transactions WHERE order_id = '850e8400-e29b-41d4-a716-446655440005'), 
     'REF-22222-001', 96.38, 'Customer requested cancellation', 'processed', 'support_agent_1', '2024-01-19 10:15:00+00');

-- Add some additional orders for more realistic data
INSERT INTO orders (id, order_number, customer_id, status, subtotal, tax_amount, shipping_amount, total_amount, payment_status, shipping_address, billing_address, created_at) VALUES
    ('850e8400-e29b-41d4-a716-446655440006', '33333', '750e8400-e29b-41d4-a716-446655440006', 'pending', 129.99, 10.40, 9.99, 150.38, 'pending',
     '{"street": "777 Maple Dr", "city": "Seattle", "state": "WA", "postal_code": "98101"}',
     '{"street": "777 Maple Dr", "city": "Seattle", "state": "WA", "postal_code": "98101"}',
     '2024-01-22 08:15:00+00'),
     
    ('850e8400-e29b-41d4-a716-446655440007', '44444', '750e8400-e29b-41d4-a716-446655440007', 'confirmed', 74.98, 6.00, 9.99, 90.97, 'paid',
     '{"street": "999 Cedar Ln", "city": "Austin", "state": "TX", "postal_code": "73301"}',
     '{"street": "999 Cedar Ln", "city": "Austin", "state": "TX", "postal_code": "73301"}',
     '2024-01-21 13:45:00+00');

-- Insert order items for additional orders
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
    ('850e8400-e29b-41d4-a716-446655440006', '650e8400-e29b-41d4-a716-446655440007', 1, 129.99, 129.99), -- Running Shoes
    ('850e8400-e29b-41d4-a716-446655440007', '650e8400-e29b-41d4-a716-446655440003', 3, 24.99, 74.97);   -- 3x Cotton T-Shirts 