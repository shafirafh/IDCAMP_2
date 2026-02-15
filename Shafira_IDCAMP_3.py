#!/usr/bin/env python
# coding: utf-8
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# Header & Title
st.header('🛍️ Dashboard Brasilia E-Commerce Dataset')
st.title("Distribution of Customers in Brazil")

# Load Dataset
order_items_dataset     = pd.read_csv('https://raw.githubusercontent.com/shafirafh/IDCAMP_2/main/order_items_dataset.csv',index_col=0)
order_payments_dataset  = pd.read_csv('https://raw.githubusercontent.com/shafirafh/IDCAMP_2/main/order_payments_dataset.csv',index_col=0)
order_reviews_dataset   = pd.read_csv('https://raw.githubusercontent.com/shafirafh/IDCAMP_2/main/order_reviews_dataset.csv',index_col=0)
orders_dataset          = pd.read_csv('https://raw.githubusercontent.com/shafirafh/IDCAMP_2/main/orders_dataset.csv',index_col=0)
product_category_name_translation   = pd.read_csv('https://raw.githubusercontent.com/shafirafh/IDCAMP_2/main/product_category_name_translation.csv',index_col=0)
products_dataset        = pd.read_csv('https://raw.githubusercontent.com/shafirafh/IDCAMP_2/main/products_dataset.csv',index_col=0)
sellers_dataset         = pd.read_csv('https://raw.githubusercontent.com/shafirafh/IDCAMP_2/main/sellers_dataset.csv',index_col=0)
customers_dataset       = pd.read_csv('https://raw.githubusercontent.com/shafirafh/IDCAMP_2/main/customers_dataset.csv',index_col=0)

# Cleaning Data
products_dataset.dropna(axis=0, inplace=True)

# Merge Data
df= pd.merge(orders_dataset, order_items_dataset, on='order_id', how='inner')
df= pd.merge(df, customers_dataset, on='customer_id', how='inner')
df= pd.merge(df, products_dataset, on='product_id', how='inner')

# ============================
# Pertanyaan 1: Produk paling laku
# ============================
grouped = df.groupby('product_category_name')['price'].sum().reset_index()
grouped = grouped.sort_values(by='price', ascending=False)
top8 = grouped.head(8)
other = pd.DataFrame({'product_category_name': ['Other'], 'price': [grouped['price'].iloc[8:].sum()]})
pie_data = pd.concat([top8, other])

fig1, ax1 = plt.subplots(figsize=(8,8))
ax1.pie(pie_data['price'], labels=pie_data['product_category_name'], autopct='%1.1f%%', startangle=140)
ax1.set_title('Total Amount per Category (Top 8 + Other)')
st.pyplot(fig1)

# ============================
# Pertanyaan 2: Jam order tinggi
# ============================
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
orders_per_month = df.groupby(df['order_purchase_timestamp'].dt.to_period('M')).size().reset_index(name='order_count')
orders_per_month['order_purchase_timestamp'] = orders_per_month['order_purchase_timestamp'].dt.to_timestamp()

fig2, ax2 = plt.subplots(figsize=(10,5))
ax2.plot(orders_per_month['order_purchase_timestamp'], orders_per_month['order_count'], marker='o')
ax2.set_xlabel('Waktu (Bulan)')
ax2.set_ylabel('Jumlah Order')
ax2.set_title('Jumlah Order per Bulan')
plt.xticks(rotation=45)
st.pyplot(fig2)

# ============================
# Pertanyaan 3: RFM Analysis
# ============================
recency_df = df.groupby(['customer_id'], as_index=False)['order_purchase_timestamp'].max()
recency_df.columns = ['customer_id','LastPurchaseDate']
now = pd.Timestamp.now()
recency_df['Recency'] = (now - recency_df['LastPurchaseDate']).dt.days

resi_count = df.groupby('customer_id', as_index=False)['order_id'].count()
resi_count.columns = ['customer_id', 'Frequency']
price_sum = df.groupby('customer_id', as_index=False)['price'].sum()
price_sum.columns = ['customer_id', 'Monetary']

rfm = recency_df.merge(resi_count, on='customer_id').merge(price_sum, on='customer_id')
rfm = rfm[rfm['Monetary'] != 0]
rfm['R'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1])
rfm['F'] = pd.cut(rfm['Frequency'], bins=[0,5,10,15,rfm['Frequency'].max()], labels=[1,2,3,4])
rfm['M'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4])
rfm['Score'] = rfm[['R','F','M']].sum(axis=1)

def categorize(score):
    if score >= 10: return 'Champions'
    elif score >= 7: return 'Loyal Customers'
    elif score >= 4: return 'Potential Loyalists / At Risk'
    else: return 'Hibernating / Lost'

rfm['Segment'] = rfm['Score'].apply(categorize)
segment_counts = rfm['Segment'].value_counts()

fig3, ax3 = plt.subplots(figsize=(8,6))
segment_counts.plot(kind='bar', color='skyblue', edgecolor='black', ax=ax3)
ax3.set_xlabel('Segment')
ax3.set_ylabel('Jumlah Pelanggan')
ax3.set_title('Distribusi Pelanggan per Segment RFM')
st.pyplot(fig3)

# ============================
# Pertanyaan 4: Persebaran Customer
# ============================
# Tentukan titik tengah
center_lat = -14.2350  # Brazil approx latitude
center_lon = -51.9253  # Brazil approx longitude

m = folium.Map(location=[center_lat, center_lon], zoom_start=4)
st_folium(m, width=700, height=500)
