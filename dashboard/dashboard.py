import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Load data
file_path = r"C:\Users\LEGION\Documents\VSCode\dashboard-interaktif\dashboard\all_data.csv"
all_df = pd.read_csv(file_path, parse_dates=['order_approved_at'])

# Konversi kolom tanggal agar dapat digunakan untuk analisis waktu
all_df["order_approved_at"] = pd.to_datetime(all_df["order_approved_at"])

# --- PREPROCESSING DATA ---

# Agregasi data untuk tren order dan revenue per bulan
trend_df = all_df.resample('M', on='order_approved_at').agg({
    "order_id": "nunique",  # Menghitung jumlah order unik
    "price": "sum"  # Menghitung total revenue
}).reset_index()
trend_df["order_approved_at"] = trend_df["order_approved_at"].dt.strftime('%Y-%m')

# Agregasi data berdasarkan kategori produk
category_revenue_df = all_df.groupby("product_category_name_english")["price"].sum().reset_index()
category_orders_df = all_df.groupby("product_category_name_english")["order_id"].count().reset_index()

# Urutkan berdasarkan nilai tertinggi
category_revenue_df = category_revenue_df.sort_values(by="price", ascending=False)
category_orders_df = category_orders_df.sort_values(by="order_id", ascending=False)

# --- STREAMLIT DASHBOARD ---

st.set_page_config(page_title="Dashboard E-Commerce", layout="wide")
st.title("📊 Dashboard E-Commerce")

# === TREN ORDER & REVENUE ===
st.subheader("📈 Tren Order & Revenue")
col1, col2 = st.columns(2)

# Pilihan rentang waktu untuk tren order & revenue
with col1:
    start_date = st.selectbox("Pilih Tanggal Awal", trend_df["order_approved_at"].unique(), index=0)
with col2:
    end_date = st.selectbox("Pilih Tanggal Akhir", trend_df["order_approved_at"].unique(), index=len(trend_df)-1)

# Filter data berdasarkan rentang waktu yang dipilih
filtered_trend_df = trend_df[(trend_df["order_approved_at"] >= start_date) & (trend_df["order_approved_at"] <= end_date)]

# Opsi tampilan jumlah pesanan dan pendapatan
show_orders = st.checkbox("Tampilkan Jumlah Pesanan", value=True)
show_revenue = st.checkbox("Tampilkan Pendapatan", value=True)

# Visualisasi tren order & revenue
fig, ax1 = plt.subplots(figsize=(12, 6))

if show_orders:
    ax1.plot(filtered_trend_df["order_approved_at"], filtered_trend_df["order_id"], marker='o', linestyle='-',
             color="#4285F4", label="Jumlah Pesanan")
    ax1.set_ylabel("Jumlah Pesanan", color="#4285F4")

if show_revenue:
    ax2 = ax1.twinx()
    ax2.plot(filtered_trend_df["order_approved_at"], filtered_trend_df["price"], marker='s', linestyle='--',
             color="#EA4335", label="Pendapatan")
    ax2.set_ylabel("Pendapatan", color="#EA4335")

ax1.set_xlabel("Periode (Tahun-Bulan)")
ax1.set_title("📈 Tren Order & Revenue")
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis="y", linestyle="--", alpha=0.7)

if show_orders:
    ax1.legend(loc="upper left")
if show_revenue:
    ax2.legend(loc="upper right")

st.pyplot(fig)

# === ANALISIS TOP & BOTTOM PRODUK ===
st.subheader("📊 Analisis Top & Bottom Products")

col1, col2 = st.columns(2)
with col1:
    top_n = st.slider("Jumlah Kategori Teratas", min_value=1, max_value=10, value=5)
with col2:
    bottom_n = st.slider("Jumlah Kategori Terbawah", min_value=1, max_value=10, value=5)

# Fungsi untuk menampilkan grafik bar atau pie
def plot_chart(data, title, xlabel, is_pie):
    fig, ax = plt.subplots(figsize=(6, 6))
    if is_pie:
        ax.pie(data.iloc[:, 1], labels=data.iloc[:, 0], autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax.set_title(title)
    else:
        sns.barplot(y=data.iloc[:, 0], x=data.iloc[:, 1], palette="coolwarm", ax=ax)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Kategori Products")
        ax.set_title(title)
        ax.invert_yaxis()
    return fig

# Menampilkan grafik Top & Bottom Revenue dan Orders
with col1:
    st.subheader("💰 Top Products Revenue")
    st.pyplot(plot_chart(category_revenue_df.sort_values(by="price", ascending=True).head(top_n), "Top Products Revenue", "Total Pendapatan", False))

with col2:
    st.subheader("💰 Bottom Products Revenue")
    st.pyplot(plot_chart(category_revenue_df.sort_values(by="price", ascending=False).head(bottom_n), "Bottom Products Revenue", "Total Pendapatan", False))

col1, col2 = st.columns(2)
with col1:
    st.subheader("🛒 Top Products Order")
    st.pyplot(plot_chart(category_orders_df.sort_values(by="order_id", ascending=True).head(top_n), "Top Products Order", "Jumlah Pesanan", False))

with col2:
    st.subheader("🛒 Bottom Products Order")
    st.pyplot(plot_chart(category_orders_df.sort_values(by="order_id", ascending=False).head(bottom_n), "Bottom Products Order", "Jumlah Pesanan", False))

# === ANALISIS KARAKTERISTIK & SEGMENTASI PELANGGAN ===
st.subheader("📌 Karakteristik & Segmentasi Pelanggan")

# Agregasi data berdasarkan lokasi pelanggan dan metode pembayaran
city_df = all_df['customer_city'].value_counts().reset_index()
city_df.columns = ['City', 'Jumlah Pelanggan']

state_df = all_df['customer_state'].value_counts().reset_index()
state_df.columns = ['State', 'Jumlah Pelanggan']

payment_df = all_df['payment_type'].value_counts().reset_index()
payment_df.columns = ['Metode Pembayaran', 'Jumlah Transaksi']

# Fungsi untuk membuat grafik batang
def plot_bar_chart(data, x_col, y_col, title, xlabel):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y=data[x_col], x=data[y_col], ax=ax, palette="coolwarm")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(x_col)
    ax.invert_yaxis()
    return fig

# Menampilkan opsi analisis pelanggan
st.subheader("📊 Opsi Tampilkan Karakteristik & Segmentasi Pelanggan")
show_city = st.checkbox("Tampilkan Distribusi Pelanggan Berdasarkan Kota", value=True)
show_state = st.checkbox("Tampilkan Distribusi Pelanggan Berdasarkan Negara Bagian", value=True)
show_payment = st.checkbox("Tampilkan Distribusi Metode Pembayaran", value=True)

# Menampilkan grafik berdasarkan opsi yang dipilih
if show_city:
    st.subheader("🏙️ Distribusi Pelanggan Berdasarkan Kota (Top 10)")
    fig = plot_bar_chart(city_df.head(10), "City", "Jumlah Pelanggan", 
                         "Top 10 Kota dengan Jumlah Pelanggan Terbanyak", 
                         "Jumlah Pelanggan")
    st.pyplot(fig)

if show_state:
    st.subheader("🌎 Distribusi Pelanggan Berdasarkan Negara Bagian (Top 5)")
    fig = plot_bar_chart(state_df.head(5), "State", "Jumlah Pelanggan", 
                         "Distribusi Pelanggan Berdasarkan State", 
                         "Jumlah Pelanggan")
    st.pyplot(fig)

if show_payment:
    st.subheader("💳 Distribusi Metode Pembayaran")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(payment_df["Jumlah Transaksi"], labels=payment_df["Metode Pembayaran"], autopct='%1.1f%%', 
           colors=plt.cm.Paired.colors, startangle=90)
    ax.set_title("Distribusi Penggunaan Metode Pembayaran")
    st.pyplot(fig)

# === ANALISIS RFM ===
st.subheader("📊 RFM (Recency, Frequency, Monetary) Analysis")

# Mengelompokkan data berdasarkan customer_id
rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
    "order_approved_at": "max",
    "order_id": "nunique",
    "price": "sum"
})

rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date

# Menghitung recency
recent_date = all_df["order_approved_at"].dt.date.max()
rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

st.write("### 📌 Ringkasan RFM Data")
st.dataframe(rfm_df.head())

# === Opsi Menampilkan Grafik ===
st.subheader("📊 Opsi Tampilkan Grafik RFM")

show_recency = st.checkbox("Tampilkan Grafik Recency", value=True)
show_frequency = st.checkbox("Tampilkan Grafik Frequency", value=True)
show_monetary = st.checkbox("Tampilkan Grafik Monetary", value=True)

# Menampilkan grafik berdasarkan pilihan pengguna
if show_recency:
    st.subheader("🔹 Top 5 Pelanggan Paling Aktif (Recency)")
    top_recency = rfm_df.sort_values(by="recency", ascending=True).head(5)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(y=top_recency["customer_id"], x=top_recency["recency"], palette="Blues_r", ax=ax)
    ax.set_title("Top 5 Pelanggan Paling Aktif (Recency)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Jumlah Hari Sejak Transaksi Terakhir")
    ax.set_ylabel("Customer ID")
    st.pyplot(fig)

if show_frequency:
    st.subheader("🔹 Top 5 Pelanggan Paling Sering Berbelanja (Frequency)")
    top_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(y=top_frequency["customer_id"], x=top_frequency["frequency"], palette="Greens_r", ax=ax)
    ax.set_title("Top 5 Pelanggan Paling Sering Berbelanja (Frequency)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Jumlah Transaksi")
    ax.set_ylabel("Customer ID")
    st.pyplot(fig)

if show_monetary:
    st.subheader("🔹 Top 5 Pelanggan dengan Total Belanja Terbesar (Monetary)")
    top_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(y=top_monetary["customer_id"], x=top_monetary["monetary"], palette="Oranges_r", ax=ax)
    ax.set_title("Top 5 Pelanggan dengan Total Belanja Terbesar (Monetary)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Total Belanja (Revenue)")
    ax.set_ylabel("Customer ID")
    st.pyplot(fig)