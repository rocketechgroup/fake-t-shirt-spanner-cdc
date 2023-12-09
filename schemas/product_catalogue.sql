-- Table: categories
CREATE TABLE categories
(
    category_id STRING(36) NOT NULL DEFAULT (GENERATE_UUID()),
    name        STRING(255) NOT NULL
) PRIMARY KEY(category_id);

-- Table: customers, unique index is email
CREATE TABLE customers
(
    customer_id  STRING(36) NOT NULL DEFAULT (GENERATE_UUID()),
    name         STRING(255) NOT NULL,
    email        STRING(255) NOT NULL,
    address      STRING(255) NOT NULL,
    phone_number STRING(255) NOT NULL
) PRIMARY KEY(customer_id);

CREATE UNIQUE NULL_FILTERED INDEX EmailIndex ON customers (email);

-- Table: products
CREATE TABLE products
(
    product_id  STRING(36) NOT NULL DEFAULT (GENERATE_UUID()),
    name        STRING(255) NOT NULL,
    description STRING(255) NOT NULL,
    price       NUMERIC NOT NULL,
    image_url   STRING(255),
    category_id STRING(36) NOT NULL,
    CONSTRAINT FK_ProductCategory FOREIGN KEY (category_id) REFERENCES categories (category_id),
) PRIMARY KEY(product_id);

-- Table: orders
CREATE TABLE orders
(
    order_id         STRING(36) NOT NULL DEFAULT (GENERATE_UUID()),
    customer_id      STRING(36) NOT NULL,
    order_date       TIMESTAMP NOT NULL,
    total_amount     NUMERIC   NOT NULL,
    shipping_address STRING(255) NOT NULL,
    billing_address  STRING(255) NOT NULL,

    CONSTRAINT FK_OrderCustomer FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
) PRIMARY KEY(order_id);

-- Table: order_items
CREATE TABLE order_items
(
    order_item_id STRING(36) NOT NULL DEFAULT (GENERATE_UUID()),
    order_id      STRING(36) NOT NULL,
    product_id    STRING(36) NOT NULL,
    quantity      INT64 NOT NULL,

    CONSTRAINT FK_ItemOrderId FOREIGN KEY (order_id) REFERENCES orders (order_id),
    CONSTRAINT FK_ItemOrderProduct FOREIGN KEY (product_id) REFERENCES products (product_id)
) PRIMARY KEY(order_item_id);