import sqlite3
import os

# Connect to database
db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
tables_sql = [
    """CREATE TABLE IF NOT EXISTS shop_category (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        slug VARCHAR(200) NOT NULL UNIQUE,
        description TEXT,
        image VARCHAR(100),
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS shop_product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        slug VARCHAR(200) NOT NULL UNIQUE,
        description TEXT NOT NULL,
        weapon_type VARCHAR(20) NOT NULL,
        manufacturer VARCHAR(100),
        caliber VARCHAR(50),
        barrel_length VARCHAR(50),
        weight VARCHAR(50),
        material VARCHAR(100),
        price DECIMAL(10,2) NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        image VARCHAR(100) NOT NULL,
        image2 VARCHAR(100),
        image3 VARCHAR(100),
        image4 VARCHAR(100),
        is_active BOOLEAN NOT NULL DEFAULT 1,
        is_popular BOOLEAN NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        category_id INTEGER NOT NULL REFERENCES shop_category(id)
    )""",
    """CREATE INDEX IF NOT EXISTS shop_produc_slug_idx ON shop_product(slug)""",
    """CREATE INDEX IF NOT EXISTS shop_produc_weapon__idx ON shop_product(weapon_type)""",
    """CREATE INDEX IF NOT EXISTS shop_produc_is_acti_idx ON shop_product(is_active, is_popular)""",
    """CREATE TABLE IF NOT EXISTS shop_order (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        email VARCHAR(254) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        address TEXT NOT NULL,
        city VARCHAR(100) NOT NULL,
        postal_code VARCHAR(20),
        payment_method VARCHAR(20) NOT NULL DEFAULT 'cash_on_delivery',
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        total_price DECIMAL(10,2) NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        user_id INTEGER REFERENCES auth_user(id)
    )""",
    """CREATE TABLE IF NOT EXISTS shop_orderitem (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quantity INTEGER NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        order_id INTEGER NOT NULL REFERENCES shop_order(id),
        product_id INTEGER NOT NULL REFERENCES shop_product(id)
    )""",
    """CREATE TABLE IF NOT EXISTS shop_userprofile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone VARCHAR(20),
        address TEXT,
        city VARCHAR(100),
        postal_code VARCHAR(20),
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id)
    )"""
]

for sql in tables_sql:
    try:
        cursor.execute(sql)
        print(f"Executed: {sql[:50]}...")
    except Exception as e:
        print(f"Error: {e}")

conn.commit()
conn.close()
print("\nAll tables created successfully!")
print("Now you can run: python manage.py create_sample_data")



