import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

st.set_page_config(page_title="Real Estate Dashboard KZ", layout="wide")

@st.cache_data
def load_data():
    cities = ['Алматы', 'Астана', 'Шымкент']
    years = pd.date_range(start='2020-01-01', end='2023-12-01', freq='MS')

    history_data = []
    for city in cities:
        base_price = 350000 if city == 'Шымкент' else (500000 if city == 'Астана' else 650000)
        for date in years:
            for rooms in [1, 2, 3]:
                price = base_price + (rooms * 20000) + (np.random.randn() * 10000) + (years.get_loc(date) * 5000)
                history_data.append([city, date, rooms, price])
    
    df_history = pd.DataFrame(history_data, columns=['City', 'Date', 'Rooms', 'Price_per_sqm'])
    
    districts = {
        'Алматы': [[43.2389, 76.9455, 800], [43.2551, 76.9126, 650], [43.2775, 76.8200, 500]],
        'Астана': [[51.1694, 71.4491, 700], [51.1283, 71.4305, 900], [51.1801, 71.4100, 550]],
        'Шымкент': [[42.3223, 69.5901, 450], [42.3150, 69.5800, 400], [42.3400, 69.6000, 380]]
    }
    
    materials_index = np.linspace(100, 180, len(years)) + np.random.normal(0, 5, len(years))
    property_index = materials_index * 1.2 + np.random.normal(0, 10, len(years))
    df_corr = pd.DataFrame({'Materials_Index': materials_index, 'Property_Price_Index': property_index})
    
    return df_history, districts, df_corr

df_history, districts, df_corr = load_data()

st.title("🏠 Қазақстан жылжымайтын мүлік нарығының аналитикасы")

st.header("1. Аудандар бойынша баға картасы (Heatmap)")
selected_city = st.selectbox("Қаланы таңдаңыз:", ['Алматы', 'Астана', 'Шымкент'])

city_coords = {'Алматы': [43.2389, 76.9455], 'Астана': [51.1694, 71.4491], 'Шымкент': [42.3223, 69.5901]}
m = folium.Map(location=city_coords[selected_city], zoom_start=12)
HeatMap(districts[selected_city]).add_to(m)
st_folium(m, width=1300, height=400)

col1, col2 = st.columns([2, 1])

with col1:
    st.header("2. Баға динамикасы (1, 2, 3 бөлмелі)")
    city_df = df_history[df_history['City'] == selected_city]
    fig_line = px.line(city_df, x='Date', y='Price_per_sqm', color='Rooms',
                      title=f"{selected_city} қаласындағы пәтерлердің м² бағасы",
                      labels={'Price_per_sqm': 'Баға (₸)', 'Rooms': 'Бөлме саны'})
    st.plotly_chart(fig_line, use_container_width=True)

    st.header("3. Құрылыс материалдары мен үй бағасының корреляциясы")
    fig_scatter = px.scatter(df_corr, x='Materials_Index', y='Property_Price_Index',
                             trendline="ols", 
                             title="Материалдар құны vs Үй бағасы",
                             labels={'Materials_Index': 'Материалдар индексі', 'Property_Price_Index': 'Үй бағасы индексі'})
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.header("4. Ипотека: 7-20-25")
    property_value = st.number_input("Пәтер құны (₸):", value=25000000, step=1000000)
    down_payment = property_value * 0.20
    loan_amount = property_value - down_payment
    
    years_loan = st.slider("Мерзімі (жыл):", 1, 25, 15)
    interest_rate = 0.07 / 12
    months = years_loan * 12
    
    monthly_payment = (loan_amount * interest_rate * (1 + interest_rate)**months) / ((1 + interest_rate)**months - 1)
    
    st.info(f"**Алғашқы жарна (20%):** {down_payment:,.0f} ₸")
    st.info(f"**Несие сомасы:** {loan_amount:,.0f} ₸")
    st.success(f"**Ай сайынғы төлем:** {monthly_payment:,.0f} ₸")
    
    st.markdown("---")
    st.subheader("Нарық статистикасы")
    st.metric("Орташа м² бағасы", f"{city_df['Price_per_sqm'].iloc[-1]:,.0f} ₸", "+5.4%")
    st.metric("Инфляция әсері", "12.5%", delta_color="inverse")