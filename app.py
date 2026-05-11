import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import os

st.title("Bryce Valley Hardware - Smart Min/Max Ordering System")
st.write("Upload your RockSolid CSV exports below. The system automatically calculates dynamic Min/Max levels based on yearly and recent velocity.")

# --- 1. SETTINGS & ALLOCATIONS ---
st.subheader("Budget Allocation")
col1, col2 = st.columns(2)
with col1:
    total_weekly_budget = st.number_input("Total Available Weekly Budget ($):", min_value=0.0, value=2804.0, step=100.0)
with col2:
    hillman_monthly_budget = st.number_input("Hillman Monthly Rep Budget ($):", min_value=0.0, value=800.0, step=100.0)

# Calculate the true DIB budget
weekly_hillman_deduction = hillman_monthly_budget / 4
dib_weekly_budget = total_weekly_budget - weekly_hillman_deduction
st.info(f"**Calculated Do It Best Budget:** ${total_weekly_budget:.2f} (Total) - ${weekly_hillman_deduction:.2f} (Weekly Hillman Reserve) = **${dib_weekly_budget:.2f}**")

# --- STRATEGY & MIN/MAX SETTINGS ---
st.subheader("Dynamic Min/Max Settings")
col3, col4, col5 = st.columns(3)
with col3:
    min_weeks = st.number_input("MIN: Safety Stock Weeks:", min_value=0.5, value=1.5, step=0.5, help="Order Trigger: When supply drops below this many weeks, order more.")
with col4:
    max_weeks = st.number_input("MAX: Order-Up-To Weeks:", min_value=1.0, value=4.0, step=0.5, help="Fill Target: How many weeks of inventory to stock the shelf with when ordering.")
with col5:
    global_min_shelf = st.number_input("Global Minimum Shelf Qty:", min_value=1, value=2, step=1, help="The absolute lowest MIN allowed for slow/new items.")

st.subheader("Outlier Protection")
col6, col7 = st.columns(2)
with col6:
    qty_cap = st.number_input("Max Qty Counted Per Receipt:", min_value=1, value=5, help="Caps bulk buys. If someone buys 12, it only counts as 5.")
with col7:
    min_receipts = st.number_input("Min Historical Receipts Required:", min_value=1, value=1, help="Set to 2 to ignore items that only sold on a single ticket last year.")

# The Exclusion Box
excluded_skus_input = st.text_input("SKUs to Exclude from Do It Best Order (comma-separated):", value="261947", placeholder="e.g., 261947, 123456")
excluded_list = [sku.strip() for sku in excluded_skus_input.split(',')] if excluded_skus_input else []

# --- 2. FILE UPLOADERS (Weekly Files Only) ---
st.subheader("Data Upload")
inv_file = st.file_uploader("1. Upload Inventory CSV (Current QOH & Costs)", type=['csv'])
sales_60_file = st.file_uploader("2. Upload Last 60 Days Sales CSV", type=['csv'])
sales_30_file = st.file_uploader("3. Upload Last Year 30 Days Sales CSV (Seasonal)", type=['csv'])

# --- 3. BULLETPROOF DATA CLEANER ---
def clean_inventory_row(row):
    desc_col_val = str(row.get('Description', '')).strip()
    
    if '$' in desc_col_val:
        desc = str(row.get('Primary Vendor', '')).strip()    
        prod_code = str(row.get('SKU', '')).strip()          
        sku = prod_code 
        qoh_str = str(row.get('Product Code', '0'))
        cost_str = str(row.get('Standard Price', '0'))
        vendor = "UNKNOWN"
    else:
        desc = desc_col_val
        sku = str(row.get('SKU', '')).strip()
        prod_code = str(row.get('Product Code', sku)).strip()
        vendor = str(row.get('Primary Vendor', 'UNKNOWN')).strip()
        qoh_str = str(row.get('Inventory', '0'))
        cost_str = str(row.get('Average Cost', '0'))
        
    qoh_float = pd.to_numeric(qoh_str, errors='coerce')
    if pd.isna(qoh_float): qoh_float = 0.0
        
    cost_str = cost_str.replace('$', '').replace(',', '').replace('(', '-').replace(')', '').strip()
    cost_float = pd.to_numeric(cost_str, errors='coerce') 

    if pd.isna(cost_float) or cost_float <= 0.0:
        cost_float = 0.01 
        
    return pd.Series([prod_code, sku, desc, vendor, "", qoh_float, cost_float])

# --- 4. CORE PROCESSING ---
if inv_file and sales_60_file and sales_30_file:
    try:
        st.write("Processing Data...")
        
        df_inv_raw = pd.read_csv(inv_file, skiprows=8)
        df_60_raw = pd.read_csv(sales_60_file, skiprows=8)
        df_30_raw = pd.read_csv(sales_30_file, skiprows=8)
        
        try:
            df_yearly_raw = pd.read_csv("yearly_sales.csv", skiprows=8)
        except FileNotFoundError:
            st.error("🚨 Missing File: I cannot find 'yearly_sales.csv'. Please make sure it is saved in the exact same folder as your app.py file!")
            st.stop()
            
        df_inv_raw.columns = df_inv_raw.columns.str.strip()
        df_60_raw.columns = df_60_raw.columns.str.strip()
        df_30_raw.columns = df_30_raw.columns.str.strip()
        df_yearly_raw.columns = df_yearly_raw.columns.str.strip()

        df_inv = df_inv_raw.apply(clean_inventory_row, axis=1)
        df_inv.columns = ['Product Code', 'SKU', 'Description', 'Vendor', 'Secondary_Vendor', 'Current_QOH', 'Unit_Cost']
        
        # FIX: Explicitly cast all Product Codes to string to prevent silent mismatching
        df_inv['Product Code'] = df_inv['Product Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_60_raw['Product Code'] = df_60_raw['Product Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_30_raw['Product Code'] = df_30_raw['Product Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_yearly_raw['Product Code'] = df_yearly_raw['Product Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        df_60_raw['Qty'] = pd.to_numeric(df_60_raw['Qty'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df_30_raw['Qty'] = pd.to_numeric(df_30_raw['Qty'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df_yearly_raw['Qty'] = pd.to_numeric(df_yearly_raw['Qty'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
        df_60_raw['Qty'] = df_60_raw['Qty'].clip(upper=qty_cap)
        df_30_raw['Qty'] = df_30_raw['Qty'].clip(upper=qty_cap)
        df_yearly_raw['Qty'] = df_yearly_raw['Qty'].clip(upper=qty_cap) 
        
        df_60 = df_60_raw.groupby('Product Code')['Qty'].sum().reset_index()
        df_60.rename(columns={'Qty': 'Qty_Sold_60_Days'}, inplace=True)
        
        df_30 = df_30_raw.groupby('Product Code').agg(
            Qty_Sold_Last_Year_30_Days=('Qty', 'sum'),
            Ticket_Count=('Qty', 'count')
        ).reset_index()
        df_30.loc[df_30['Ticket_Count'] < min_receipts, 'Qty_Sold_Last_Year_30_Days'] = 0
        df_30.drop(columns=['Ticket_Count'], inplace=True)
        
        df_yearly = df_yearly_raw.groupby('Product Code')['Qty'].sum().reset_index()
        df_yearly.rename(columns={'Qty': 'Qty_Sold_Yearly'}, inplace=True)
        
        df_master = pd.merge(df_inv, df_60, on='Product Code', how='left')
        df_master = pd.merge(df_master, df_30, on='Product Code', how='left')
        df_master = pd.merge(df_master, df_yearly, on='Product Code', how='left')
        
        df_master['Qty_Sold_60_Days'] = df_master['Qty_Sold_60_Days'].fillna(0)
        df_master['Qty_Sold_Last_Year_30_Days'] = df_master['Qty_Sold_Last_Year_30_Days'].fillna(0)
        df_master['Qty_Sold_Yearly'] = df_master['Qty_Sold_Yearly'].fillna(0)
        df_master['Current_QOH'] = df_master['Current_QOH'].fillna(0)
        
        df_master.loc[df_master['Product Code'] == 'H', 'Description'] = 'Misc hardware'
        df_master.loc[df_master['Product Code'] == 'H', 'Vendor'] = 'Hillman' 

        is_hillman = (
            df_master['Vendor'].str.lower().str.contains('hillman', na=False) | 
            df_master['Secondary_Vendor'].str.lower().str.contains('hillman', na=False) |
            df_master['Description'].str.lower().str.contains('misc hardware', na=False)
        )
        df_normal = df_master[~is_hillman].copy()

        # --- 6. THE DYNAMIC MIN/MAX MATH FUNCTION ---
        def calculate_optimal_order(df_subset, budget_limit, exclusions, min_wks, max_wks, global_min):
            if df_subset.empty: return df_subset
            
            df_subset['SKU'] = df_subset['SKU'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_subset = df_subset[df_subset['SKU'].str.match(r'^\d{6}$', na=False)]
            
            if exclusions:
                df_subset = df_subset[~df_subset['SKU'].isin(exclusions)]
            if df_subset.empty: return df_subset
            
            df_subset['Vel_60'] = df_subset['Qty_Sold_60_Days'] / 8.5
            df_subset['Vel_30'] = df_subset['Qty_Sold_Last_Year_30_Days'] / 4.3
            df_subset['Vel_Year'] = df_subset['Qty_Sold_Yearly'] / 52.0
            
            df_subset['Peak_Velocity'] = df_subset[['Vel_60', 'Vel_30', 'Vel_Year']].max(axis=1)
            
            df_subset['Calculated_Min'] = (df_subset['Peak_Velocity'] * min_wks).clip(lower=global_min).apply(np.ceil)
            
            df_subset['Calculated_Max'] = (df_subset['Peak_Velocity'] * max_wks).clip(lower=df_subset['Calculated_Min'] + 1).apply(np.ceil)
            
            df_subset['Order_Qty'] = np.where(
                df_subset['Current_QOH'] <= df_subset['Calculated_Min'],
                df_subset['Calculated_Max'] - df_subset['Current_QOH'],
                0
            )
            
            df_subset = df_subset[df_subset['Order_Qty'] > 0].copy()
            if df_subset.empty: return df_subset
            
            df_subset['Unit_Cost'] = df_subset['Unit_Cost'].replace(0, 0.01)
            df_subset['Line_Item_Cost'] = df_subset['Order_Qty'] * df_subset['Unit_Cost']
            
            def get_priority(row):
                if row['Peak_Velocity'] >= 0.1:
                    return 100000 + (row['Peak_Velocity'] / row['Unit_Cost'])
                elif row['Peak_Velocity'] > 0:
                    return 10000 + row['Qty_Sold_Yearly']
                else:
                    return -1000  

            df_subset['Priority_Score'] = df_subset.apply(get_priority, axis=1)
            
            df_subset = df_subset.sort_values(by='Priority_Score', ascending=False)
            df_subset['Cumulative_Cost'] = df_subset['Line_Item_Cost'].cumsum()
            
            final_cart = df_subset[df_subset['Cumulative_Cost'] <= budget_limit].copy()
            
            return final_cart[final_cart['Priority_Score'] > -500].copy()

        # RUN THE ALGORITHM
        normal_order = calculate_optimal_order(df_normal, dib_weekly_budget, excluded_list, min_weeks, max_weeks, global_min_shelf)

        # --- 7. EXPORT FOR DO IT BEST ---
        def generate_dib_csv(df_final):
            df_export = pd.DataFrame()
            df_export['SKU'] = df_final['SKU']
            df_export['OrderQuantity'] = df_final['Order_Qty'].astype(int)
            df_export['MemberRetail'] = ''
            df_export['PromoBulletin'] = ''
            return df_export.to_csv(index=False).encode('utf-8')

        today_str = date.today().strftime("%Y-%m-%d")

        if not normal_order.empty:
            st.success(f"Do It Best Order Total: ${normal_order['Line_Item_Cost'].sum():.2f} (Total Items: {len(normal_order)})")
            st.download_button(
                "Download Do It Best Weekly Order", 
                data=generate_dib_csv(normal_order), 
                file_name=f"DoItBest_Weekly_{today_str}.csv", 
                mime="text/csv"
            )
        else:
            st.warning("No items qualified for the Do It Best Weekly Order.")

    except Exception as e:
        st.error(f"Error processing files: {e}")