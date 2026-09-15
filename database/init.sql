-- ============================================
-- Simple Notebook Store Database
-- ============================================

CREATE TABLE IF NOT EXISTS notebooks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    pages INTEGER DEFAULT 100,
    stock INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO notebooks (title, brand, price, pages, stock, description) VALUES
('Classic Ruled Notebook', 'Moleskine', 899.00, 240, 50, 'Premium hardcover with ruled pages'),
('Dotted Journal', 'Leuchtturm1917', 1299.00, 251, 35, 'Perfect for bullet journaling'),
('Spiral Notebook', 'Rhodia', 449.00, 160, 100, 'Wire-bound with perforated pages'),
('Leather Journal', 'Peter Pauper', 1899.00, 192, 25, 'Handcrafted leather journal'),
('Graph Paper Notebook', 'Muji', 299.00, 160, 150, 'Minimalist 5mm squares');

SELECT 'Database initialized!' AS message;
