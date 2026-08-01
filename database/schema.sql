CREATE TABLE categories (
    category_id     SERIAL PRIMARY KEY,
    category_name   VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(200) NOT NULL,
    category_id     INTEGER NOT NULL REFERENCES categories(category_id),
    price           NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    stock_quantity  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    city            VARCHAR(100),
    signup_date     DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE orders (
    order_id        SERIAL PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date      DATE NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'completed'
);

CREATE TABLE order_items (
    order_item_id   SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(order_id),
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(12, 2) NOT NULL
);

CREATE TABLE reviews (
    review_id       SERIAL PRIMARY KEY,
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_date     DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);