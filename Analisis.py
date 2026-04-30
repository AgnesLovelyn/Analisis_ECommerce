import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# ===== LANGKAH 1: Load Data =====
df = pd.read_csv('data_penjualan.csv')
print(df.head())

# ===== LANGKAH 2: Inspeksi & Pembersihan Data =====
print("\n=== INFO DATA ===")
print(df.info())

print("\n=== DATA KOSONG ===")
print(df.isnull().sum())

df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df = df.dropna(subset=['Total_Sales'])
print("\nData setelah dibersihkan:", df.shape)

# ===== LANGKAH 3: Tren Penjualan Bulanan =====
df['Month'] = df['Order_Date'].dt.to_period('M').astype(str)
monthly_sales = df.groupby('Month')['Total_Sales'].sum()

plt.figure(figsize=(10, 5))
plt.plot(monthly_sales.index, monthly_sales.values, marker='o', color='b')
plt.title('Tren Penjualan Bulanan')
plt.xlabel('Bulan')
plt.ylabel('Total Penjualan (Rp)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('grafik_tren_bulanan.png')
plt.show()

# ===== LANGKAH 4: Penjualan per Kategori =====
category_sales = df.groupby('Product_Category')['Total_Sales'].sum().sort_values()

plt.figure(figsize=(8, 5))
category_sales.plot(kind='barh', color='orange')
plt.title('Total Penjualan per Kategori Produk')
plt.xlabel('Total Penjualan (Rp)')
plt.tight_layout()
plt.savefig('grafik_kategori.png')
plt.show()

# ===== LANGKAH 5: Heatmap Korelasi =====
correlation = df[['Total_Sales', 'Ad_Budget', 'Quantity']].corr()

plt.figure(figsize=(6, 4))
sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title('Peta Korelasi Antar Variabel')
plt.tight_layout()
plt.savefig('grafik_heatmap.png')
plt.show()

# ===== LANGKAH 6: RFM Analysis =====
snapshot_date = df['Order_Date'].max() + dt.timedelta(days=1)

rfm = df.groupby('CustomerID').agg({
    'Order_Date': lambda x: (snapshot_date - x.max()).days,
    'Order_ID': 'count',
    'Total_Sales': 'sum'
})

rfm.columns = ['Recency', 'Frequency', 'Monetary']
rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm['RFM_Group'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

print("\n=== HASIL RFM ===")
print(rfm.head(10))

# ===== LANGKAH 7: Regresi Linear =====
X = df[['Ad_Budget']]
y = df['Total_Sales']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

print(f"\nKoefisien Iklan: {model.coef_[0]}")
print(f"Akurasi Model (R2 Score): {model.score(X_test, y_test)}")

# ===== LANGKAH 8: Scatter Plot Regresi =====
plt.figure(figsize=(8, 5))
plt.scatter(X_test, y_test, color='blue', label='Data Aktual', alpha=0.6)
plt.plot(X_test, model.predict(X_test), color='red', label='Garis Regresi')
plt.title('Pengaruh Budget Iklan terhadap Total Penjualan')
plt.xlabel('Ad Budget (Rp)')
plt.ylabel('Total Sales (Rp)')
plt.legend()
plt.tight_layout()
plt.savefig('grafik_regresi.png')
plt.show()

# ===== TUGAS 1: Identifikasi Produk (Dummy Inventory) =====
np.random.seed(42)
df['Inventory'] = np.random.randint(10, 200, size=len(df))

df_6bulan = df[df['Order_Date'] >= '2023-07-01']

produk = df_6bulan.groupby('Product_Category').agg(
    Total_Terjual=('Quantity', 'sum'),
    Rata_Inventory=('Inventory', 'mean')
).reset_index()

plt.figure(figsize=(8, 5))
plt.scatter(produk['Rata_Inventory'], produk['Total_Terjual'],
            color='green', s=200)

for i, row in produk.iterrows():
    plt.annotate(row['Product_Category'],
                (row['Rata_Inventory'], row['Total_Terjual']),
                textcoords="offset points", xytext=(8, 5))

plt.title('Identifikasi Produk: Stok vs Volume Penjualan (6 Bulan Terakhir)')
plt.xlabel('Rata-rata Stok (Inventory)')
plt.ylabel('Total Jumlah Terjual')
plt.tight_layout()
plt.savefig('grafik_identifikasi_produk.png')
plt.show()

# ===== TUGAS 3: Analisis Geografis (Dummy Wilayah) =====
wilayah_list = ['Jawa Timur', 'Jawa Barat', 'Jawa Tengah',
                'DKI Jakarta', 'Sumatera Utara']
np.random.seed(42)
df['Wilayah'] = np.random.choice(wilayah_list, size=len(df))
df['Profit'] = df['Total_Sales'] - df['Ad_Budget']

wilayah_profit = df.groupby('Wilayah')['Profit'].sum().sort_values()

plt.figure(figsize=(8, 5))
wilayah_profit.plot(kind='barh', color='tomato')
plt.title('Profit Margin per Wilayah (Terendah ke Tertinggi)')
plt.xlabel('Total Profit (Rp)')
plt.tight_layout()
plt.savefig('grafik_geografis.png')
plt.show()

# ===== TUGAS 4: Uji Hipotesis Diskon (Dummy Discount) =====
np.random.seed(42)
df['Discount_Percentage'] = np.random.randint(0, 50, size=len(df))

df['Discount_Group'] = df['Discount_Percentage'].apply(
    lambda x: 'Diskon > 20%' if x > 20 else 'Diskon ≤ 20%'
)

group_stats = df.groupby('Discount_Group').agg(
    Rata_Total_Sales=('Total_Sales', 'mean'),
    Rata_Quantity=('Quantity', 'mean'),
    Jumlah_Transaksi=('Order_ID', 'count')
).reset_index()

print("\n=== UJI HIPOTESIS DISKON ===")
print(group_stats)

plt.figure(figsize=(8, 5))
plt.bar(group_stats['Discount_Group'],
        group_stats['Rata_Total_Sales'],
        color=['steelblue', 'salmon'])
plt.title('Rata-rata Penjualan: Diskon > 20% vs Diskon ≤ 20%')
plt.xlabel('Kelompok Diskon')
plt.ylabel('Rata-rata Total Sales (Rp)')
plt.tight_layout()
plt.savefig('grafik_hipotesis_diskon.png')
plt.show()