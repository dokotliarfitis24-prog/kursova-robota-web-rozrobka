#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weapons_shop.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

# Check if tables exist
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'shop_%'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    print(f"Existing shop tables: {existing_tables}")

# Try to apply migrations
try:
    call_command('migrate', 'shop', verbosity=2)
except Exception as e:
    print(f"Error: {e}")
    # If migration doesn't work, create tables manually
    from django.core.management.sql import sql_create_index, sql_create_table
    from shop.models import Category, Product, Order, OrderItem, UserProfile
    
    print("\nTrying to create tables manually...")
    with connection.cursor() as cursor:
        # Create Category table
        if 'shop_category' not in existing_tables:
            cursor.execute("""
                CREATE TABLE shop_category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    slug VARCHAR(200) NOT NULL UNIQUE,
                    description TEXT,
                    image VARCHAR(100),
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """)
            print("Created shop_category table")
        
        # Create Product table
        if 'shop_product' not in existing_tables:
            cursor.execute("""
                CREATE TABLE shop_product (
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
                    stock INTEGER UNSIGNED NOT NULL DEFAULT 0,
                    image VARCHAR(100) NOT NULL,
                    image2 VARCHAR(100),
                    image3 VARCHAR(100),
                    image4 VARCHAR(100),
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    is_popular BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    category_id INTEGER NOT NULL REFERENCES shop_category(id)
                )
            """)
            cursor.execute("CREATE INDEX shop_produc_slug_idx ON shop_product(slug)")
            cursor.execute("CREATE INDEX shop_produc_weapon__idx ON shop_product(weapon_type)")
            cursor.execute("CREATE INDEX shop_produc_is_acti_idx ON shop_product(is_active, is_popular)")
            print("Created shop_product table")
        
        # Create Order table
        if 'shop_order' not in existing_tables:
            cursor.execute("""
                CREATE TABLE shop_order (
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
                )
            """)
            print("Created shop_order table")
        
        # Create OrderItem table
        if 'shop_orderitem' not in existing_tables:
            cursor.execute("""
                CREATE TABLE shop_orderitem (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quantity INTEGER UNSIGNED NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    order_id INTEGER NOT NULL REFERENCES shop_order(id),
                    product_id INTEGER NOT NULL REFERENCES shop_product(id)
                )
            """)
            print("Created shop_orderitem table")
        
        # Create UserProfile table
        if 'shop_userprofile' not in existing_tables:
            cursor.execute("""
                CREATE TABLE shop_userprofile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone VARCHAR(20),
                    address TEXT,
                    city VARCHAR(100),
                    postal_code VARCHAR(20),
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id)
                )
            """)
            print("Created shop_userprofile table")
        
        connection.commit()
        print("\nAll tables created successfully!")



