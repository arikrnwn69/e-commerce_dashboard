import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
import matplotlib.pyplot as plt

# Judul Aplikasi
st.title("Dashboard Analisis Data E-Commerce")

st.markdown("""
1. **Bagaimana Pola Pembelian Pelanggan?**

   - Tujuan: Memahami produk yang paling sering dibeli, kategori produk populer, dan waktu puncak pembelian.

2. **Produk Apa Saja yang Memberikan Keuntungan Tertinggi?**

   - Tujuan: Mengidentifikasi produk atau kategori dengan kontribusi pendapatan terbesar.
3. **Bagaimana segmentasi pelanggan sejauh ini?**
    - Tujuan : Untuk melihat seberapa banyak pelanggan yang memiliki value yang tinggi
               dengan memahami pelanggan berdasarkan RFM / Recency Frekuensi Monetary

4. **Wilayah Mana saja yang memiliki Pelanggan dengan order terbanyak?**
            
    - Tujuan : Untuk memahami terkait potensi pada tiap masing masing kota / Wilayah 

""")

# Set Path File
file_path = "./data/"

# Fungsi untuk Load dan Preprocess Data
@st.cache_data
def load_and_preprocess_data(file_name):
    data = pd.read_csv(file_path + file_name)
    data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'], errors='coerce')
    data = data.dropna(subset=['order_purchase_timestamp'])
    data['order_purchase_day'] = data['order_purchase_timestamp'].dt.day
    data['order_purchase_month'] = data['order_purchase_timestamp'].dt.month_name()
    return data

# Load Data
populer_product = pd.read_csv(file_path + 'populer_product.csv')
freq_buyer = pd.read_csv(file_path + 'freq_buyer.csv', index_col=0)
retensi_pembelian = load_and_preprocess_data('retensi_pembelian.csv')
customer_segment = pd.read_csv(file_path + 'customer_segment.csv')
cust_city = pd.read_csv(file_path + 'cust_city.csv')
customer_rfm = pd.read_csv(file_path + 'customer_rfm.csv')
profit_product = pd.read_csv(file_path + 'profit_product.csv')




# **1. Produk Paling Populer**

st.header("1. Pertanyaan Pertama")
st.subheader("Produk Paling Populer")
populer_product = populer_product.sort_values(by='Jumlah Pemesanan', ascending=False)

chart_popular = alt.Chart(populer_product[0:25]).mark_bar().encode(
    x='Jumlah Pemesanan:Q',
    y=alt.Y('product_category_name:N', sort='-x')
).properties(title='Produk Paling Populer')

st.dataframe(populer_product)
st.altair_chart(chart_popular, use_container_width=True)

# **2. Frekuensi Pembelian Berdasarkan Product ID**
st.subheader("Frekuensi Pembelian Berdasarkan Product ID")
freq_buyer = freq_buyer.sort_values(by='Frekuensi Pembelian', ascending=False)
freq_buyer = freq_buyer.reset_index(drop=True)  # Reset indeks lama
freq_buyer.index += 1

chart_freq = alt.Chart(freq_buyer[0:20]).mark_bar().encode(
    x='Frekuensi Pembelian:Q',
    y=alt.Y('product_id:N', sort='-x'),
    color='product_category_name:N'
).properties(
    title='Frekuensi Pembelian Untuk 20 Produk Teratas Berdasarkan Product ID',
    width=1000,
    height=500
)

st.dataframe(freq_buyer)
st.altair_chart(chart_freq, use_container_width=True)

# **3. Retensi Pembelian: Jumlah Pembelian per Bulan dan Tanggal**
st.subheader("Retensi Pembelian")

# Analisis Bulanan
monthly_trend = retensi_pembelian.groupby('order_purchase_month').agg({'order_id': 'count'}).reset_index()
monthly_trend.columns = ['Bulan', 'Jumlah Pembelian']

# Analisis Harian
daily_sales = retensi_pembelian.groupby('order_purchase_day').agg({'order_id': 'count'}).reset_index()
daily_sales.columns = ['Tanggal', 'Jumlah Pembelian']

# Visualisasi Bulanan
chart_monthly = alt.Chart(monthly_trend).mark_bar().encode(
    x=alt.X('Bulan:N', sort=None),
    y='Jumlah Pembelian:Q',
    color=alt.Color('Jumlah Pembelian:Q', scale=alt.Scale(scheme='viridis'))
).properties(title='Jumlah Pembelian per Bulan', width=500)

# Visualisasi Harian
chart_daily = alt.Chart(daily_sales).mark_line(point=True).encode(
    x=alt.X('Tanggal:O'),
    y='Jumlah Pembelian:Q',
    color=alt.value('blue')
).properties(title='Pola Pembelian Berdasarkan Tanggal', width=500)

# Tampilan Berdampingan
col1, col2 = st.columns(2)
with col1:
    st.altair_chart(chart_monthly, use_container_width=True)
with col2:
    st.altair_chart(chart_daily, use_container_width=True)

# **4. Tambahan Interaktivitas: Filter Rentang Tanggal**
st.sidebar.header("Filter Data")

# Widget untuk memilih rentang tanggal
start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal:",
    value=[
        retensi_pembelian['order_purchase_timestamp'].min().to_pydatetime().date(),
        retensi_pembelian['order_purchase_timestamp'].max().to_pydatetime().date()
    ]
)

# Filter data berdasarkan rentang tanggal
filtered_data = retensi_pembelian[
    (retensi_pembelian['order_purchase_timestamp'] >= pd.Timestamp(start_date)) &
    (retensi_pembelian['order_purchase_timestamp'] <= pd.Timestamp(end_date))
]

# Agregasi jumlah pembelian per hari
filtered_daily_sales = (
    filtered_data.groupby(filtered_data['order_purchase_timestamp'].dt.date)
    .agg({'order_id': 'count'})
    .reset_index()
    .rename(columns={'order_purchase_timestamp': 'Tanggal', 'order_id': 'Jumlah Pembelian'})
)

# Menampilkan informasi rentang tanggal
st.write(f"Data setelah filter ({start_date} hingga {end_date}):")
st.dataframe(filtered_data)

# Membuat line chart
chart_line = alt.Chart(filtered_daily_sales).mark_line(point=True).encode(
    x=alt.X('Tanggal:T', title='Tanggal'),
    y=alt.Y('Jumlah Pembelian:Q', title='Jumlah Pembelian'),
    tooltip=['Tanggal', 'Jumlah Pembelian']
).properties(
    title='Jumlah Pembelian Harian Berdasarkan Rentang Tanggal',
    width=800,
    height=400
)

st.altair_chart(chart_line, use_container_width=True)

# **5. Product Apa Yang Menghasilkan Keuntungan Tertinggi
st.header("2. Pertanyaan Ke Dua")

st.subheader("Product Apa Yang Memberikan Keuntungan Tertinggi?")
chart_profit = alt.Chart(profit_product[0:20]).mark_bar().encode(
    x=alt.X('Total Profit:Q', title='Total Profit (Rupiah)'),
    y=alt.Y('product_category_name:N', sort='-x', title='Kategori Produk'),
    color=alt.Color('Jumlah Produk:Q', scale=alt.Scale(scheme='viridis'), title='Jumlah Produk'),
    tooltip=['product_category_name', 'Jumlah Produk', 'Total Profit']
).properties(
    title="Kategori Produk dengan Pendapatan Tertinggi",
    width=800,
    height=400
)

# Menampilkan tabel dan chart
st.dataframe(profit_product)
st.altair_chart(chart_profit, use_container_width=True)

# **6. Mengkategorikan pelanggan berdasarkan Skor RFM
st.title("3. Pertanyaan Ketiga")
st.subheader("Bagaimana Segmentasi Pelanggan?")

# Subtitle
st.subheader("Distribusi Segmen Pelanggan")

# Sidebar untuk pengaturan chart
st.sidebar.header("Pengaturan Visualisasi")
bar_width = st.sidebar.slider("Lebar Chart (px)", min_value=500, max_value=1200, value=800, step=50)

# Pastikan data memiliki kolom yang benar
if 'customer_segment' in customer_segment.columns and 'customer_unique_id' in customer_segment.columns:
    # Membuat chart dengan Altair
    chart = alt.Chart(customer_segment).mark_bar().encode(
        x=alt.X('customer_segment:N', sort=None, axis=alt.Axis(labelAngle=45)),
        y=alt.Y('customer_unique_id:Q', title="Jumlah Customer Unique ID")
    ).properties(
        title="Distribusi Jumlah Pelanggan per Segmen",
        width=800,
        height=400
    )
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.error("Kolom 'customer_segment' atau 'jumlah_pelanggan' tidak ditemukan pada data.")

# Tabel data
st.write("### Data Pelanggan")
st.dataframe(customer_segment)

# Insight tambahan
st.write("### Insight")
st.markdown(
    """
    - **Pelanggan Bernilai Rendah** memiliki jumlah pelanggan terbanyak (**63,205 pelanggan**).
    - **Pelanggan Teratas** memiliki jumlah pelanggan paling sedikit (**934 pelanggan**).
    - Proporsi pelanggan terbesar berada di segmen **nilai rendah**, sementara segmen **pelanggan teratas** memiliki jumlah yang jauh lebih kecil.
    """
)

# **7. Peta Pydeck: Distribusi Pemesanan**
st.title("Pertanyaan Tambahan")
st.subheader("Distribusi Pemesanan Berdasarkan Lokasi")

cust_city = cust_city[cust_city['order_count'] > 10]

# Definisikan Layer untuk Pydeck
cust_city['radius'] = cust_city['order_count'] * 500
cust_city['fill_color'] = cust_city['order_count'].apply(
    lambda x: [max(0, 255 - x * 5), 100, 150, 160]
)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=cust_city,
    get_position=["geolocation_lng", "geolocation_lat"],
    get_radius="radius",
    get_fill_color="fill_color",
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=cust_city["geolocation_lat"].mean(),
    longitude=cust_city["geolocation_lng"].mean(),
    zoom=4,
    pitch=0,
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{geolocation_city}: {order_count} orders"},
)

st.pydeck_chart(r)


