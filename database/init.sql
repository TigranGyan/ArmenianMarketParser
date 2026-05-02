-- Stores
CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website_url VARCHAR(500),
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Categories (taxonomy)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    parent_id INT REFERENCES categories(id),
    slug VARCHAR(255) UNIQUE
);

-- Normalized Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    canonical_name VARCHAR(500) NOT NULL,
    brand VARCHAR(255),
    category_id INT REFERENCES categories(id),
    attributes JSONB,
    ean VARCHAR(13),
    image_url VARCHAR(1000),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Prices with history
CREATE TABLE prices (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id),
    store_id INT NOT NULL REFERENCES stores(id),
    price NUMERIC(10,2) NOT NULL,
    old_price NUMERIC(10,2),
    currency CHAR(3) DEFAULT 'AMD',
    url VARCHAR(1000) NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT now(),
    valid_to TIMESTAMPTZ,
    UNIQUE (product_id, store_id, valid_from)
);

CREATE INDEX idx_prices_product ON prices(product_id) WHERE valid_to IS NULL;
CREATE INDEX idx_prices_store ON prices(store_id, product_id);
CREATE INDEX idx_prices_valid ON prices(valid_to, valid_from);

-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    notification_prefs JSONB
);

-- Shopping Lists
CREATE TABLE shopping_lists (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    name VARCHAR(255),
    items JSONB
);

-- Seed initial store
INSERT INTO stores (name, website_url) VALUES ('SAS', 'https://www.sas.am');
