# src/generate_synthetic_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid

np.random.seed(42)
random.seed(42)

n = 2000  # number of orders

start_date = datetime(2024,1,1)
order_dates = [start_date + timedelta(days=int(x)) for x in np.random.exponential(scale=60, size=n).cumsum() % 365]

regions = ['North', 'South', 'East', 'West', 'Central']
warehouses = ['WH-A','WH-B','WH-C','WH-D']
product_categories = ['Electronics','Apparel','Home','Office','Accessories']
carriers = ['Carrier A','Carrier B','Carrier C','Carrier D']

rows = []
for i in range(n):
    order_id = f"ORD-{str(uuid.uuid4())[:8]}"
    od = order_dates[i]
    # ship_date: 0-7 days after order, sometimes null
    ship_delay = np.random.poisson(lam=1.5)
    ship_date = od + timedelta(days=int(ship_delay))
    # delivery_date: add transit 1-10 days; sometimes late or missing
    transit = np.random.randint(1,10)
    delivery_date = ship_date + timedelta(days=transit) if np.random.rand() > 0.02 else pd.NaT
    status = random.choices(['Delivered','Backorder','Cancelled','Shipped'], weights=[0.78,0.08,0.03,0.11])[0]
    if status == 'Backorder':
        delivery_date = pd.NaT
    region = random.choice(regions)
    wh = random.choice(warehouses)
    cat = random.choice(product_categories)
    price = round(abs(np.random.normal(80, 40)),2)
    qty = int(np.random.choice([1,1,1,2,3,4]))
    delay_reason = ''
    if status == 'Delivered' and delivery_date and (delivery_date - od).days > 10:
        delay_reason = random.choice(['Carrier Delay','Inventory Shortage','Weather','Fulfillment Issue'])
    carrier = random.choice(carriers)
    rows.append({
        'order_id': order_id,
        'order_date': od.strftime('%Y-%m-%d'),
        'ship_date': ship_date.strftime('%Y-%m-%d') if pd.notnull(ship_date) else '',
        'delivery_date': delivery_date.strftime('%Y-%m-%d') if pd.notnull(delivery_date) else '',
        'region': region,
        'warehouse': wh,
        'product_category': cat,
        'unit_price': price,
        'quantity': qty,
        'order_status': status,
        'delay_reason': delay_reason,
        'carrier': carrier
    })

df = pd.DataFrame(rows)
df.to_csv('data/raw/orders_raw.csv', index=False)
print("Generated data/raw/orders_raw.csv with", len(df), "rows")
