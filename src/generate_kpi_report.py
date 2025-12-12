# src/generate_kpi_report.py
import pandas as pd

def monthly_kpis(df):
    df['order_month'] = df['order_date'].dt.to_period('M').dt.to_timestamp()
    # On-time: delivered and order_to_delivery_days <= 7
    delivered = df[df['order_status']=='Delivered']
    kpis = delivered.groupby('order_month').agg(
        total_orders = ('order_id','count'),
        ontime = (lambda x: (delivered['is_late']==False).groupby(delivered['order_month']).sum()),
    )
    return kpis

def main():
    df = pd.read_csv('data/cleaned/orders_cleaned.csv', parse_dates=['order_date','ship_date','delivery_date'])
    # Basic KPIs
    df['is_delivered'] = df['order_status']=='Delivered'
    df['is_ontime'] = df['is_delivered'] & (df['order_to_delivery_days']<=7)
    # Monthly aggregations
    df['order_month'] = df['order_date'].dt.to_period('M').dt.to_timestamp()
    monthly = df.groupby('order_month').agg(
        total_orders = ('order_id','count'),
        delivered = ('is_delivered','sum'),
        ontime = ('is_ontime','sum'),
        avg_order_to_delivery_days = ('order_to_delivery_days','mean')
    ).reset_index()
    monthly['ontime_pct'] = (monthly['ontime'] / monthly['delivered']).fillna(0).round(3)
    # Overall KPIs
    overall = {
        'total_orders': int(df['order_id'].nunique()),
        'delivered': int(df['is_delivered'].sum()),
        'ontime_pct_overall': float((df['is_ontime'].sum() / max(1, df['is_delivered'].sum())).round(3))
    }
    monthly.to_excel('reports/monthly_kpi_report.xlsx', index=False)
    pd.DataFrame([overall]).to_csv('reports/overall_kpis.csv', index=False)
    print("Saved reports/monthly_kpi_report.xlsx and reports/overall_kpis.csv")

if __name__ == '__main__':
    main()
