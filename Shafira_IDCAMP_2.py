#!/usr/bin/env python
# coding: utf-8
import streamlit as st

st.header('🛍️ Dashboard Brasilia E-Commerce Dataset')

st.title("Distribution of Customers in Brazil")
# # Proyek Analisis Data: Nama dataset
# - Nama: Shafira Faira Huwaida
# - Email: shafirafaira.2019@student.uny.ac.id
# - Id Dicoding: shaf_faira

# ## Menentukan Pertanyaan Bisnis

# - pertanyaan 1
# produk apa saja yang paling laku?
# 
# - pertanyaan 2
# Jam berapa order tinggi?
# 
# - pertanyaan 3
# Bagaimana RFM pelanggan?
# 
# - pertanyaan 4
# bagaimana persebaran customer?

# ## Menyiapkan semua library yang dibutuhkan

# In[1]:


#!pip install streamlit
#!pip install folium


# In[2]:


import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import folium


# ## Data Wrangling

# ### Gathering Data

# In[3]:


geolocation_dataset     = pd.read_csv('geolocation_dataset.csv')
order_items_dataset     = pd.read_csv('order_items_dataset.csv')
order_payments_dataset  = pd.read_csv('order_payments_dataset.csv')
order_reviews_dataset   = pd.read_csv('order_reviews_dataset.csv')
orders_dataset          = pd.read_csv('orders_dataset.csv')
product_category_name_translation   = pd.read_csv('product_category_name_translation.csv')
products_dataset        = pd.read_csv('products_dataset.csv')
sellers_dataset         = pd.read_csv('sellers_dataset.csv')
customers_dataset       = pd.read_csv('customers_dataset.csv')
#pd.read_csv('https://raw.githubusercontent.com/shafirafh/E-Commerce-Public-Dataset/main/order_reviews_dataset.csv',index_col=0)

# In[4]:


order_items_dataset.columns


# In[5]:


order_payments_dataset.columns


# In[6]:


order_reviews_dataset.columns


# In[7]:


orders_dataset.columns


# In[8]:


product_category_name_translation.columns


# In[9]:


products_dataset.columns


# In[10]:


sellers_dataset.columns


# In[11]:


customers_dataset.head()


# ### Assessing Data

# In[12]:


geolocation_dataset.isnull().sum()


# In[13]:


# Sample customer data with latitude and longitude
customers_dataset.isnull().sum()


# In[14]:


sellers_dataset.isnull().sum()


# In[15]:


products_dataset.isnull().sum()


# In[16]:


product_category_name_translation.isnull().sum()


# In[17]:


orders_dataset.isnull().sum()


# In[18]:


order_reviews_dataset.isnull().sum()


# In[19]:


order_items_dataset.isnull().sum()


# In[20]:


order_reviews_dataset.isnull().sum()


# In[21]:


order_reviews_dataset.describe


# In[22]:


order_payments_dataset.isnull().sum()


# In[23]:


order_items_dataset.isnull().sum()


# ### Cleaning Data

# In[24]:


products_dataset.isna().sum()


# In[25]:


products_dataset.dropna(axis=0, inplace=True)
products_dataset


# In[26]:


customers_dataset.head(3)


# In[27]:


geolocation_dataset = geolocation_dataset.drop_duplicates(subset=['geolocation_zip_code_prefix'])


# In[28]:


geolocation_dataset['geolocation_lat'] = geolocation_dataset['geolocation_lat'].astype(float)
geolocation_dataset['geolocation_lng'] = geolocation_dataset['geolocation_lng'].astype(float)
geolocation_dataset = geolocation_dataset.dropna(subset=['geolocation_lat','geolocation_lng'])


# ### Featuring Engineer

# In[29]:


# Gabungkan berdasarkan order_id
df= pd.merge(orders_dataset, order_items_dataset, on='order_id', how='inner')
df= pd.merge(df, customers_dataset, on='customer_id', how='inner')
df= pd.merge(df, products_dataset, on='product_id', how='inner')

df = pd.merge(
    df,
    geolocation_dataset,
    left_on='customer_zip_code_prefix',
    right_on='geolocation_zip_code_prefix',
    how='left'
)

df.head(5)


# In[30]:


#df.to_excel('df.xlsx')


# ## Exploratory Data Analysis (EDA)

# In[31]:


df.info()


# In[32]:


df.duplicated().sum()


# ## Visualization & Explanatory Analysis

# ### pertanyaan 1 - kategori produk apa saja yang paling laku?

# In[33]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[34]:


df['product_category_name'].nunique()


# In[35]:


# Group by category lalu jumlahkan price
grouped = df.groupby('product_category_name')['price'].sum().reset_index()

# Urutkan descending
grouped = grouped.sort_values(by='price', ascending=False)

# Ambil 8 kategori teratas
top8 = grouped.head(8)

# Gabungkan sisanya jadi "Other"
other = pd.DataFrame({
    'product_category_name': ['Other'],
    'price': [grouped['price'].iloc[8:].sum()]
})

# Gabungkan top8 + other
pie_data = pd.concat([top8, other])

# Buat pie chart
plt.figure(figsize=(8,8))
plt.pie(
    pie_data['price'],
    labels=pie_data['product_category_name'],
    autopct='%1.1f%%',
    startangle=140
)
plt.title('Total Amount per Category (Top 8 + Other)')
plt.show()


# ### pertanyaan 2-Jam berapa order tinggi?

# In[36]:


# Misalnya df punya kolom order_purchase_timestamp
# Pastikan kolom waktu dalam format datetime
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# Group by per bulan (bisa juga per hari atau per minggu)
orders_per_month = df.groupby(df['order_purchase_timestamp'].dt.to_period('M'))['order_id'].count()

# Ubah ke DataFrame agar lebih mudah di-plot
orders_per_month = orders_per_month.reset_index()
orders_per_month['order_purchase_timestamp'] = orders_per_month['order_purchase_timestamp'].dt.to_timestamp()

# Buat grafik
plt.figure(figsize=(10,5))
plt.plot(orders_per_month['order_purchase_timestamp'], orders_per_month['order_id'], marker='o')
plt.xlabel('Waktu (Bulan)')
plt.ylabel('Jumlah Order')
plt.title('Jumlah Order per Bulan')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ### pertanyaan 3-Bagaimana RFM pelanggan?

# In[37]:


df['customer_id'].nunique()


# #### Recency -> seberapa banyak waktu berkunjung belakangan/baru-baru inin pelanggan untuk membeli (pembelian yang baru menunjukkan low-recency).

# In[38]:


#Group by berdasarkan customer terakhir membeli
recency_df = df.groupby(['customer_id'], as_index=False)['order_purchase_timestamp'].max()
recency_df.columns = ['customer_id','LastPurchaseDate']
recency_df.tail()


# In[39]:


# Ambil waktu sekarang sebagai Timestamp
now = pd.Timestamp.now()
# Gabungkan kembali ke df utama atau buat dataframe baru
recency_df['Recency'] = (now - recency_df['LastPurchaseDate']).dt.days


# In[40]:


recency_df['Recency'] = recency_df['Recency'].astype('Int64')
recency_df.tail()


# In[41]:


recency_df['Recency'].describe()


# #### Frecuency -> seberapa banyak/jumlah mereka melakukan pembelian (pembelian yang tinggi berarti high-frecuency)

# In[42]:


# Gabungkan dengan recency_df
frequency_df = df.copy()
frequency_df.drop_duplicates(
    subset=['order_purchase_timestamp','order_id'], 
    keep='first', 
    inplace=True
)


# In[43]:


# Hitung jumlah nomor resi per pelanggan
resi_count = df.groupby('customer_id', as_index=False)['order_id'].count()
resi_count.columns = ['customer_id', 'Frequency']

frequency_df = frequency_df.merge(resi_count, on='customer_id', how='left')
frequency_df = frequency_df.sort_values(by='Frequency', ascending=False)

frequency_df.head()


# In[44]:


link_target = "fc3d1daec319d62d49bfb5e1f83123e9" 
freq_value = frequency_df.loc[frequency_df['customer_id'] == link_target, 'Frequency'] 
freq_value


# #### Monetary = seberapa banyak uang yang mereka spend untuk membeli (spend yang tinggi berarti high monetary)

# In[45]:


# Gabungkan dengan recency_df

monetary_df = df.copy()
monetary_df.drop_duplicates(
    subset=['order_purchase_timestamp','order_id'], 
    keep='first', 
    inplace=True
)


# In[46]:


# Hitung total price per customer
price_sum = df.groupby('customer_id', as_index=False)['price'].sum()
price_sum.columns = ['customer_id', 'Monetary']

# Gabungkan dengan df utama
monetary_df = df.merge(price_sum, on='customer_id', how='left')

# Urutkan berdasarkan kolom 'Monetary'
monetary_df = monetary_df.sort_values(by='Monetary', ascending=False)

# Tampilkan hasil
monetary_df.head()


# In[47]:


#Merging above tables
rf = recency_df.merge(frequency_df , left_on = 'customer_id', right_on = 'customer_id')
rfm = rf.merge(monetary_df , left_on = 'customer_id', right_on = 'customer_id' )
rfm.set_index('customer_id' , inplace = True)


# In[48]:


rfm[['Recency','Frequency','Monetary']].describe()


# In[49]:


rfm.tail()


# In[50]:


# Hapus baris dengan MOnetary = 0
rfm = rfm[rfm['Monetary'] != 0]

# Tampilkan hasil
rfm.tail()


# Recency
# <br>-Sangat baru (≤2800)<br>- Baru (2801–3000)<br>- Lama (3001–3200)<br>- Sangat lama (>3200)
# 

# Frequency
# <br>- Sangat jarang (≤5)<br>- Jarang (6–10)<br>- Sering (11–15)<br>- Sangat sering (>15)
# 

# Monetary
# <br>-  Rendah (≤500)<br>- Sedang (501–2000)<br>- Tinggi (2001–5000)<br>- Sangat tinggi (>5000)
# 

# In[51]:


# Recency
rfm['R'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1])

rfm['F'] = pd.cut(
    rfm['Frequency'],
    bins=[0, 5, 10, 15, rfm['Frequency'].max()],
    labels=[1,2,3,4]
)

rfm['M'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4])


# In[52]:


# Hapus baris jika kolom 'R' kosong
rfm = rfm.dropna(subset=['R'])


# In[53]:


rfm['Score'] = rfm[['R','F','M']].sum(axis=1)


# In[54]:


rfm.shape


# In[55]:


rfm.head()


# In[56]:


def categorize(score):
    if score >= 10:
        return 'Champions'
    elif score >= 7:
        return 'Loyal Customers'
    elif score >= 4:
        return 'Potential Loyalists / At Risk'
    else:
        return 'Hibernating / Lost'

rfm['Segment'] = rfm['Score'].apply(categorize)


# In[57]:


# Hitung jumlah pelanggan per segmen
segment_counts = rfm['Segment'].value_counts()

# Buat barchart
plt.figure(figsize=(8,6))
segment_counts.plot(kind='bar', color='skyblue', edgecolor='black')

plt.xlabel('Segment')
plt.ylabel('Jumlah Pelanggan')
plt.title('Distribusi Pelanggan per Segment RFM')
plt.xticks(rotation=45)
plt.show()


# ### pertanyaan 4-bagaimana persebaran customer?

# In[ ]:


# Tentukan titik tengah (misalnya rata-rata koordinat)
center_lat = df['geolocation_lat'].mean()
center_lon = df['geolocation_lng'].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

# Tambahkan marker untuk setiap customer
df_clean = df.dropna(subset=['geolocation_lat', 'geolocation_lng'])

for _, row in df_clean.iterrows():
    folium.Marker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        popup=f"Customer: {row['customer_id']}<br>Kota: {row['geolocation_city']}",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(m)

m


# In[2]:


#!pip install jupyter


