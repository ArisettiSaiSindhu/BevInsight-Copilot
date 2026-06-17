import sqlite3
import os
from app.config import settings

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row  # Return results as dictionary-like objects
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Product Master Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT NOT NULL,
        pack_size_ml INTEGER NOT NULL,
        unit_price REAL NOT NULL
    );
    """)
    
    # 2. Store Master Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stores (
        store_id TEXT PRIMARY KEY,
        store_name TEXT NOT NULL,
        region TEXT NOT NULL,
        city TEXT NOT NULL,
        store_format TEXT NOT NULL
    );
    """)
    
    # 3. Sales & Promotions Table (Weekly)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_promotions (
        week_start_date TEXT NOT NULL,
        product_id TEXT NOT NULL,
        store_id TEXT NOT NULL,
        region TEXT NOT NULL,
        units_sold INTEGER NOT NULL,
        revenue REAL NOT NULL,
        promotion_flag INTEGER NOT NULL,  -- 0 or 1
        promotion_type TEXT,
        discount_pct REAL,
        PRIMARY KEY (week_start_date, product_id, store_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (store_id) REFERENCES stores (store_id)
    );
    """)
    
    # 4. Inventory Table (Weekly)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        week_start_date TEXT NOT NULL,
        product_id TEXT NOT NULL,
        store_id TEXT NOT NULL,
        opening_stock INTEGER NOT NULL,
        units_received INTEGER NOT NULL,
        units_sold INTEGER NOT NULL,
        closing_stock INTEGER NOT NULL,
        stockout_flag INTEGER NOT NULL,  -- 0 or 1
        PRIMARY KEY (week_start_date, product_id, store_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (store_id) REFERENCES stores (store_id)
    );
    """)
    
    # Add indexes for performance optimization
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_week ON sales_promotions (week_start_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_prod ON sales_promotions (product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_store ON sales_promotions (store_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_week ON inventory (week_start_date);")
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")

if __name__ == "__main__":
    init_db()
