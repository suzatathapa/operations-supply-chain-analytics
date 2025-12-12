# src/clean_data.py
import pandas as pd
from dateutil import parser

def safe_parse_date(x):
    try:
        if pd.isna(x) or x == '':
            return pd.NaT
        return pd.to_datetime(x)
    except:
        return pd.NaT

def main():
    df = pd.read_csv('data/raw/orders_raw.csv')
    # Parse dates
    for c in ['order_date','ship_date','delivery_date']:
        df[c] = df[c].apply(safe_parse_date)

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=['order_id'])
    after = len(df)
    print(f"dropped {before-after} duplicate rows")

    # Standardize strings
    df['region'] = df['region'].str.title().fillna('Unknown')
    df['warehouse'] = df['warehouse'].str.upper().fillna('UNKNOWN')
    df['product_category'] = df['product_category'].str.title().fillna('Unknown')
    df['carrier'] = df['carrier'].fillna('Unknown')

    # Calculate derived fields
    df['order_to_ship_days'] = (df['ship_date'] - df['order_date']).dt.days
    df['ship_to_delivery_days'] = (df['delivery_date'] - df['ship_date']).dt.days
    df['order_to_delivery_days'] = (df['delivery_date'] - df['order_date']).dt.days

    # Flag delays
    df['is_late'] = False
    df.loc[(df['order_status']=='Delivered') & (df['order_to_delivery_days']>7), 'is_late'] = True

    # Data quality flags
    df['missing_delivery'] = df['delivery_date'].isna()
    df['missing_ship'] = df['ship_date'].isna()
    df['price_ok'] = df['unit_price'] > 0

    # Save cleaned
    df.to_csv('data/cleaned/orders_cleaned.csv', index=False)
    # Simple data quality summary
    dq = {
        'rows': len(df),
        'missing_delivery': int(df['missing_delivery'].sum()),
        'missing_ship': int(df['missing_ship'].sum()),
        'late_deliveries': int(df['is_late'].sum()),
        'invalid_prices': int((~df['price_ok']).sum())
    }
    print("Data Quality Summary:", dq)
    pd.DataFrame([dq]).to_csv('reports/data_quality_summary.csv', index=False)
    print("Saved data/cleaned/orders_cleaned.csv and reports/data_quality_summary.csv")

if __name__ == '__main__':
    main()
