import os
import sqlite3
import random
from datetime import datetime, timedelta
from app.config import settings
from app.database import init_db, get_db_connection

# Set seed for reproducibility
random.seed(42)

# Define static masters
PRODUCTS = [
    ("P001", "SparkleCola Classic", "SparkleCola", "Carbonated", "Cola", 330, 1.50),
    ("P002", "SparkleCola Zero", "SparkleCola", "Carbonated", "Cola", 330, 1.60),
    ("P003", "SparkleCola Cherry", "SparkleCola", "Carbonated", "Cola", 330, 1.75),
    ("P004", "CitrusFizz Lemon", "CitrusFizz", "Carbonated", "Lemon-Lime", 500, 1.80),
    ("P005", "CitrusFizz Orange", "CitrusFizz", "Carbonated", "Orange", 500, 1.80),
    ("P006", "CitrusFizz Tropical", "CitrusFizz", "Carbonated", "Tropical", 500, 2.00),
    ("P007", "HydroBoost Blue", "HydroBoost", "Energy Drink", "Isotonic", 250, 2.50),
    ("P008", "HydroBoost Red", "HydroBoost", "Energy Drink", "Taurine", 250, 2.50),
    ("P009", "HydroBoost SugarFree", "HydroBoost", "Energy Drink", "Isotonic", 250, 2.75),
    ("P010", "PureBrew Espresso", "PureBrew", "Coffee", "RTD Coffee", 200, 3.00),
    ("P011", "PureBrew Latte", "PureBrew", "Coffee", "RTD Coffee", 250, 3.25),
    ("P012", "PureBrew ColdBrew", "PureBrew", "Coffee", "RTD Coffee", 300, 3.50),
    ("P013", "LeafyTeas Green Tea", "LeafyTeas", "Tea", "RTD Green Tea", 500, 2.20),
    ("P014", "LeafyTeas Iced Peach", "LeafyTeas", "Tea", "RTD Black Tea", 500, 2.20),
    ("P015", "LeafyTeas Lemon Tea", "LeafyTeas", "Tea", "RTD Black Tea", 500, 2.10),
    ("P016", "OrchardFresh Apple", "OrchardFresh", "Juice", "Fruit Juice", 1000, 4.00),
    ("P017", "OrchardFresh Orange", "OrchardFresh", "Juice", "Fruit Juice", 1000, 4.20),
    ("P018", "OrchardFresh Mango", "OrchardFresh", "Juice", "Fruit Juice", 1000, 4.50),
    ("P019", "AquaPure Still", "AquaPure", "Water", "Mineral Water", 1000, 1.00),
    ("P020", "AquaPure Sparkling", "AquaPure", "Water", "Mineral Water", 750, 1.30)
]

STORES = [
    # North Region
    ("S001", "North Star Hypermarket", "North", "Chicago", "Hypermarket"),
    ("S002", "Windy City Supermarket", "North", "Chicago", "Supermarket"),
    ("S003", "Metro Express Loop", "North", "Chicago", "Convenience"),
    ("S004", "New York Central Super", "North", "New York", "Supermarket"),
    ("S005", "Times Square Mart", "North", "New York", "Convenience"),
    ("S006", "Boston Hub Hypermarket", "North", "Boston", "Hypermarket"),
    ("S007", "Harvard Square Goods", "North", "Boston", "Supermarket"),
    ("S008", "Detroit Metro Store", "North", "Detroit", "Supermarket"),
    ("S009", "Lakeside Foods", "North", "Milwaukee", "Supermarket"),
    ("S010", "Twin Cities Mega", "North", "Minneapolis", "Hypermarket"),
    
    # South Region
    ("S011", "Atlanta Plaza Super", "South", "Atlanta", "Supermarket"),
    ("S012", "Peach State Express", "South", "Atlanta", "Convenience"),
    ("S013", "Miami Beach Market", "South", "Miami", "Supermarket"),
    ("S014", "Ocean Drive Convenience", "South", "Miami", "Convenience"),
    ("S015", "Lone Star Hypermarket", "South", "Houston", "Hypermarket"),
    ("S016", "Space City Supermarket", "South", "Houston", "Supermarket"),
    ("S017", "Dallas Galleria Foods", "South", "Dallas", "Supermarket"),
    ("S018", "Austin Tech Grocers", "South", "Austin", "Supermarket"),
    
    # West Region
    ("S019", "Golden Gate Super", "West", "San Francisco", "Supermarket"),
    ("S020", "Silicon Valley Hyper", "West", "San Jose", "Hypermarket"),
    ("S021", "Pacific Heights Mart", "West", "San Francisco", "Convenience"),
    ("S022", "Angel City Mega Mall", "West", "Los Angeles", "Hypermarket"),
    ("S023", "Venice Beach Corner", "West", "Los Angeles", "Convenience"),
    ("S024", "Seattle Rain Groceries", "West", "Seattle", "Supermarket"),
    ("S025", "Portland Green Market", "West", "Portland", "Supermarket"),
    
    # East Region
    ("S026", "Philly Liberty Grocer", "East", "Philadelphia", "Supermarket"),
    ("S027", "Capitol Hill Market", "East", "Washington D.C.", "Supermarket"),
    ("S028", "Dupont Circle Express", "East", "Washington D.C.", "Convenience"),
    ("S029", "Baltimore Harbor Hyper", "East", "Baltimore", "Hypermarket"),
    ("S030", "Pitt Steel Supermarket", "East", "Pittsburgh", "Supermarket")
]

def generate_synthetic_data():
    """Generates 24 weeks of history, populates Master and Fact tables, and implements business rules."""
    print("Starting data generation...")
    init_db()  # Ensure database and tables are created
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert Product Master
    cursor.executemany("""
    INSERT OR REPLACE INTO products (product_id, product_name, brand, category, sub_category, pack_size_ml, unit_price)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, PRODUCTS)
    
    # Insert Store Master
    cursor.executemany("""
    INSERT OR REPLACE INTO stores (store_id, store_name, region, city, store_format)
    VALUES (?, ?, ?, ?, ?);
    """, STORES)
    
    # Generate 24 weeks of data
    start_date = datetime(2026, 1, 4)  # Starting on a Sunday
    weeks = 24
    
    # Keep track of inventories to carry over opening stock
    # Key: (store_id, product_id) -> closing_stock
    inventory_tracking = {}
    
    # Pre-populate initial stock for all store-product combinations
    for store in STORES:
        store_id = store[0]
        for prod in PRODUCTS:
            product_id = prod[0]
            # Initial stock: Hypermarkets hold more, coffee/cola holds more
            base_stock = 300 if store[4] == "Hypermarket" else (150 if store[4] == "Supermarket" else 60)
            inventory_tracking[(store_id, product_id)] = random.randint(base_stock - 20, base_stock + 50)
            
    sales_rows = []
    inventory_rows = []
    
    for w in range(weeks):
        week_date = start_date + timedelta(weeks=w)
        week_str = week_date.strftime("%Y-%m-%d")
        print(f"Generating data for week: {week_str} ({w + 1}/{weeks})")
        
        for store in STORES:
            store_id, store_name, region, city, store_format = store
            
            for prod in PRODUCTS:
                product_id, product_name, brand, category, sub_category, pack_size_ml, unit_price = prod
                
                # 1. Base Demand Calculation
                # Format multiplier
                format_mult = 3.0 if store_format == "Hypermarket" else (1.5 if store_format == "Supermarket" else 0.5)
                # Category popularity
                cat_popularity = 1.2 if category in ["Carbonated", "Energy Drink"] else 0.9
                # Base units
                base_units = random.randint(15, 40) * format_mult * cat_popularity
                
                # 2. Regional Demand Profiles
                regional_multiplier = 1.0
                if region == "South":
                    if category == "Tea" or brand == "CitrusFizz":
                        regional_multiplier = 1.4  # Iced Tea / citrus drinks perform great in hot climates
                elif region == "North":
                    if category == "Coffee" or brand == "SparkleCola":
                        regional_multiplier = 1.35 # Coffee / cola performs great in North
                elif region == "West":
                    if category == "Energy Drink" or category == "Juice":
                        regional_multiplier = 1.4  # Energy drinks & healthy juices perform great in the West
                elif region == "East":
                    # Balanced but slightly higher water sales
                    if category == "Water":
                        regional_multiplier = 1.2
                        
                demand = base_units * regional_multiplier
                
                # 3. Promotions & Discounts (15%-50% increase in sales)
                # 12% probability of a product being on promotion in a store in a given week
                promotion_flag = 1 if random.random() < 0.12 else 0
                promotion_type = None
                discount_pct = 0.0
                promo_uplift = 1.0
                
                if promotion_flag:
                    promo_choice = random.choice([
                        ("Discount 10%", 10.0, random.uniform(1.15, 1.22)), # 15%-22% uplift
                        ("Discount 20%", 20.0, random.uniform(1.23, 1.32)), # 23%-32% uplift
                        ("Discount 30%", 30.0, random.uniform(1.33, 1.45)), # 33%-45% uplift
                        ("Discount 50%", 50.0, random.uniform(1.46, 1.75)), # 46%-75% uplift (Deep discount)
                        ("BOGO", 50.0, random.uniform(1.50, 1.85))          # Buy One Get One is 50% discount per unit in bulk, huge uplift
                    ])
                    promotion_type, discount_pct, promo_uplift = promo_choice
                
                demand = int(demand * promo_uplift)
                
                # 4. Inventory Tracking & Stockout logic
                opening_stock = inventory_tracking[(store_id, product_id)]
                
                # Weekly replenishment logic
                # Normally, we receive replenishment. If we have low stock, we receive more.
                target_stock = 250 if store_format == "Hypermarket" else (120 if store_format == "Supermarket" else 50)
                # Some delivery variance: 10% chance of delayed/reduced shipment, which might lead to stockout
                shipment_issue = random.random() < 0.08
                
                if opening_stock < target_stock * 0.4:
                    # Low stock triggers high replenishment
                    units_received = int(target_stock * random.uniform(0.8, 1.2))
                else:
                    # Regular replenishment
                    units_received = int(max(0, target_stock - opening_stock) * random.uniform(0.6, 1.0))
                    
                if shipment_issue:
                    units_received = int(units_received * 0.2)  # Received only 20% of replenishment due to logistics issue
                
                total_available = opening_stock + units_received
                
                # Calculate sales and stockouts
                stockout_flag = 0
                if total_available <= 0:
                    units_sold = 0
                    stockout_flag = 1
                    closing_stock = 0
                elif total_available < demand:
                    # Demand exceeds stock -> Stockout occurs!
                    units_sold = total_available
                    stockout_flag = 1
                    closing_stock = 0
                else:
                    units_sold = demand
                    closing_stock = total_available - units_sold
                
                # Carry forward closing stock as next week's opening stock
                inventory_tracking[(store_id, product_id)] = closing_stock
                
                # Calculate revenue
                # Revenue = units_sold * unit_price * (1 - discount_pct / 100)
                base_revenue = units_sold * unit_price
                discount_amount = base_revenue * (discount_pct / 100.0)
                revenue = round(base_revenue - discount_amount, 2)
                
                # Append to records
                sales_rows.append((
                    week_str, product_id, store_id, region, units_sold, revenue,
                    promotion_flag, promotion_type, discount_pct
                ))
                
                inventory_rows.append((
                    week_str, product_id, store_id, opening_stock, units_received,
                    units_sold, closing_stock, stockout_flag
                ))
                
    # Insert facts into database
    print(f"Writing {len(sales_rows)} sales rows and {len(inventory_rows)} inventory rows to database...")
    cursor.executemany("""
    INSERT INTO sales_promotions (week_start_date, product_id, store_id, region, units_sold, revenue, promotion_flag, promotion_type, discount_pct)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, sales_rows)
    
    cursor.executemany("""
    INSERT INTO inventory (week_start_date, product_id, store_id, opening_stock, units_received, units_sold, closing_stock, stockout_flag)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, inventory_rows)
    
    conn.commit()
    conn.close()
    print("Database population completed successfully!")

if __name__ == "__main__":
    generate_synthetic_data()
