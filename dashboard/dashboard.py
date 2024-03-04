import pandas as pd
import plotly.express as px
import streamlit as st

order_item_data = pd.read_csv('../data/olist_order_items_dataset.csv')
order_review_data = pd.read_csv('../data/olist_order_reviews_dataset.csv')
order_data = pd.read_csv('./order_data_cleaned.csv')
product_data = pd.read_csv('./product_data_cleaned.csv')



min_date = pd.to_datetime(order_data['order_approved_at']).min()
max_date = pd.to_datetime(order_data['order_approved_at']).max()

with st.sidebar:
    st.markdown('Dataset from: [Olist E-Commerce Public Dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce)')
    st.image("https://d3hw41hpah8tvx.cloudfront.net/images/logo_olist_d7309b5f20.png")

    start_date, end_date = st.date_input(
        label='Pilih rentang waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

order_data_filtered = order_data[
    (pd.to_datetime(order_data['order_approved_at']) >= pd.to_datetime(start_date)) &
    (pd.to_datetime(order_data['order_approved_at']) <= pd.to_datetime(end_date))
]

monthly_orders = order_data_filtered.groupby(pd.to_datetime(order_data_filtered['order_approved_at']).dt.date).size().reset_index(name='total_orders')

order_item_product_category = pd.merge(
    order_item_data,
    product_data,
    how='left',
    on='product_id'
)

order_item_product_category = pd.merge(
    order_item_product_category,
    order_data,
    how='left',
    on='order_id'
)

order_item_product_category['order_year'] = pd.to_datetime(order_item_product_category['order_approved_at']).dt.to_period('Y')
trending_product = order_item_product_category.groupby(['product_category_name_english', 'order_year']).size().reset_index(name='count').sort_values(by='order_year', ascending=True)
years = trending_product['order_year'].unique()
year_total = trending_product.groupby('order_year')['count'].transform('sum')
trending_product['percentage'] = trending_product['count'] / year_total * 100
trending_product.loc[trending_product['percentage'] < 4, 'product_category_name_english'] = 'others'
trending_product = trending_product.groupby(['product_category_name_english', 'order_year']).sum().reset_index().sort_values(by='count', ascending=False)

order_review_data = pd.merge(
    order_data[['order_id','is_ontime']],
    order_review_data[['order_id', 'review_score']],
    how='left',
    on='order_id'
)

order_review_data = order_review_data.groupby(['review_score', 'is_ontime']).size().reset_index(name='count')

st.header('Proyek Analisis Data: E-Commerce Public Dataset')

st.markdown('''
            - **Nama:** Dimas Fawwaz Prabowo Kusumaji
            - **Email:** dfawwazpk@outlook.com
            - **ID Dicoding:** dfawwazpk
            - **Study Group:** ML-60
            ''')

st.subheader(f'Tren Penjualan dari {start_date} hingga {end_date}')

col1, col2 = st.columns(2)

with col1:
    st.metric('Total pesanan', value=order_data_filtered.shape[0])

with col2:
    st.metric('Rata-rata waktu pemrosesan', value="%.f hari" % order_data_filtered['order_days_taken'].mean())

line_chart = px.line(
    monthly_orders,
    x="order_approved_at",
    y="total_orders",
).update_layout(
    xaxis_title="Tanggal Pesanan",
    yaxis_title="Jumlah Pesanan"
)

st.plotly_chart(line_chart)

st.subheader(f'Persentase Penjualan Berdasarkan Kategori Produk Tiap Tahun')

for year in years:
    year_data = trending_product[trending_product['order_year'] == year]
    pie_chart = px.pie(
        trending_product,
        values=year_data['count'],
        names=year_data['product_category_name_english'],
        title=f'Tahun {year}',
    )

    st.plotly_chart(pie_chart)

st.subheader('Review Produk Berdasarkan Ketepatan Waktu Pengiriman')

bar_chart = px.bar(
    order_review_data,
    x="review_score",
    y="count",
    color="is_ontime",
    barmode='group',
).update_layout(
    xaxis_title="Rating",
    yaxis_title="Jumlah Pesanan",
)

st.plotly_chart(bar_chart)

st.caption('Copyright © 2024 Dimas Fawwaz Prabowo Kusumaji')