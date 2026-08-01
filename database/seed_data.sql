INSERT INTO categories (category_name) VALUES
('Electronics'), ('Books'), ('Home & Kitchen'), ('Sports'), ('Beauty');

INSERT INTO products (product_name, category_id, price, stock_quantity) VALUES
('Wireless Mouse', 1, 15.99, 120),
('Mechanical Keyboard', 1, 49.99, 80),
('Bluetooth Speaker', 1, 29.99, 60),
('Data Science Handbook', 2, 22.50, 200),
('Clean Code', 2, 18.00, 150),
('Non-stick Frying Pan', 3, 25.00, 90),
('Electric Kettle', 3, 19.99, 70),
('Yoga Mat', 4, 14.00, 100),
('Running Shoes', 4, 55.00, 65),
('Face Moisturizer', 5, 12.50, 130);

INSERT INTO customers (full_name, email, city, signup_date) VALUES
('Nguyen Van A', 'a.nguyen@example.com', 'Hanoi', '2025-01-15'),
('Tran Thi B', 'b.tran@example.com', 'Ho Chi Minh', '2025-02-20'),
('Le Van C', 'c.le@example.com', 'Da Nang', '2025-03-05'),
('Pham Thi D', 'd.pham@example.com', 'Hanoi', '2025-04-10'),
('Hoang Van E', 'e.hoang@example.com', 'Hai Phong', '2025-05-18');

INSERT INTO orders (customer_id, order_date, status) VALUES
(1, '2025-06-01', 'completed'),
(2, '2025-06-03', 'completed'),
(1, '2025-06-15', 'completed'),
(3, '2025-07-02', 'completed'),
(4, '2025-07-10', 'completed'),
(5, '2025-07-20', 'completed');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 2, 15.99),
(1, 4, 1, 22.50),
(2, 2, 1, 49.99),
(3, 3, 1, 29.99),
(4, 5, 3, 18.00),
(5, 6, 1, 25.00),
(6, 9, 1, 55.00);

INSERT INTO reviews (product_id, customer_id, rating, review_date) VALUES
(1, 1, 5, '2025-06-05'),
(2, 2, 4, '2025-06-06'),
(4, 1, 5, '2025-06-16'),
(9, 5, 4, '2025-07-22');