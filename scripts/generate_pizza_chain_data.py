import random
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

# Config
NUM_ORDERS = 1000
NUM_CUSTOMERS = 100
NUM_STORES = 20
NUM_SKUS = 50
MAX_ITEMS_PER_ORDER = 5
DAYS_HISTORY = 20

# Output Directory
output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

# 1. SKU Master
print("Generating SKU Master...")
print("Generating SKU Master...")
# Realistic pizza chain item names
item_catalog = {
    "Margherita Pizza": "Pizza",
    "Pepperoni Pizza": "Pizza",
    "Veggie Supreme": "Pizza",
    "BBQ Chicken Pizza": "Pizza",
    "Paneer Tikka Pizza": "Pizza",
    "Cheese Burst Pizza": "Pizza",
    "Hawaiian Pizza": "Pizza",
    "Meat Lovers": "Pizza",
    "Tandoori Paneer Pizza": "Pizza",
    "Mushroom Pizza": "Pizza",
    "Classic Cheese Pizza": "Pizza",

    "Spicy Chicken Wings": "Sides",
    "Garlic Breadsticks": "Sides",
    "Cheesy Nachos": "Sides",
    "Green Salad": "Sides",
    "Chicken Tenders": "Sides",

    "Soft Drink (Cola)": "Drinks",
    "Soft Drink (Orange)": "Drinks",

    "Chocolate Lava Cake": "Desserts"
}

sku_master = []
for i, (item_name, category) in enumerate(item_catalog.items(), 1):
    sku_master.append({
        "sku_id": f"SKU{i:04}",
        "item_name": item_name,
        "category": category,
        "price": round(random.uniform(5.0, 15.0), 2),
        "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d %H:%M:%S")
    })
sku_df = pd.DataFrame(sku_master)
sku_df.to_csv(output_dir / "sku_master.csv", index=False)
sku_price_map = {row["sku_id"]: row["price"] for row in sku_master}
sku_ids = list(sku_price_map.keys())

# 2. Discounts
print("Generating Discounts...")
discounts = [
    {"discount_code": "DISC10", "discount_amount": 10.0},
    {"discount_code": "DISC5", "discount_amount": 5.0},
    {"discount_code": None, "discount_amount": 0.0}
]
discount_df = pd.DataFrame(discounts)
discount_df.to_csv(output_dir / "discounts_applied.csv", index=False)

# 3. Orders and Order Items
print("Generating Orders and Order Items...")
orders = []
order_items = []
start_date = datetime.now() - timedelta(days=DAYS_HISTORY)

for i in range(1, NUM_ORDERS + 1):
    order_id = f"ORD{i:07}"
    order_time = start_date + timedelta(minutes=random.randint(0, DAYS_HISTORY * 24 * 60))
    store_id = random.randint(1, NUM_STORES)
    customer_id = random.randint(1, NUM_CUSTOMERS)

    total_amount = 0.0
    num_items = random.randint(1, MAX_ITEMS_PER_ORDER)

    for _ in range(num_items):
        sku_id = random.choice(sku_ids)
        quantity = random.randint(1, 3)
        price = sku_price_map[sku_id]
        discount = random.choice(discounts)
        discount_amount = discount["discount_amount"]
        subtotal = max((price * quantity) - discount_amount, 0.0)

        order_items.append({
            "order_id": order_id,
            "sku_id": sku_id,
            "quantity": quantity,
            "unit_price": price,
            "discount_code": discount["discount_code"],
            "discount_amount": discount_amount
        })
        total_amount += subtotal

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "store_id": store_id,
        "order_time": order_time,
        "total_amount": round(total_amount, 2)
    })

orders_df = pd.DataFrame(orders)
orders_df.to_csv(output_dir / "orders.csv", index=False)

order_items_df = pd.DataFrame(order_items)
order_items_df.to_csv(output_dir / "order_items.csv", index=False)

# 4. Inventory Logs
print("Generating Inventory Logs...")
inventory_logs = []
log_days = [start_date + timedelta(days=d) for d in range(DAYS_HISTORY)]

for log_day in log_days:
    for store_id in range(1, NUM_STORES + 1):
        for sku_id in sku_ids:
            inventory_logs.append({
                "log_time": log_day,
                "store_id": store_id,
                "sku_id": sku_id,
                "current_stock": random.randint(0, 100),
                "restock_threshold": 10
            })

inventory_logs_df = pd.DataFrame(inventory_logs)
inventory_logs_df.to_csv(output_dir / "inventory_logs.csv", index=False)

print(f"\n✅ Done. Files generated in: {output_dir.resolve()}")
