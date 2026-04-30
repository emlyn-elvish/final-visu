import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Global Air Quality Dashboard", layout="wide")

# 1. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("AQI and Lat Long of Countries.csv")
    # Basic cleaning
    df = df.dropna(subset=['Country'])
    # Create Hemisphere column
    df['Hemisphere'] = df['lat'].apply(lambda x: 'Northern' if x >= 0 else 'Southern')
    return df

df = load_data()

# 2. Sidebar Filters
st.sidebar.header("Filter Options")

# Country Multi-select
countries = sorted(df['Country'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries:", 
    options=countries, 
    default=["United States of America", "China", "India", "Brazil"]
)

# AQI Category Multi-select
categories = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
selected_categories = st.sidebar.multiselect("Select AQI Categories:", options=categories, default=categories)

# Filter the dataframe based on selection
mask = (df['Country'].isin(selected_countries)) & (df['AQI Category'].isin(selected_categories))
filtered_df = df[mask]

# 3. Main Dashboard Layout
st.title("🌍 Global Air Quality Analysis Dashboard")
st.markdown("Exploring real-world AQI data and pollutants across the globe.")

# Row 1: Key Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cities", len(filtered_df))
col2.metric("Avg AQI", f"{filtered_df['AQI Value'].mean():.1f}")
col3.metric("Max AQI", filtered_df['AQI Value'].max())
col4.metric("Countries", len(filtered_df['Country'].unique()))

st.divider()

# Row 2: Interactive Map
st.subheader("📍 Geospatial Distribution of Air Quality")
fig_map = px.scatter_mapbox(
    filtered_df, 
    lat="lat", 
    lon="lng", 
    color="AQI Category",
    size="AQI Value",
    hover_name="City", 
    hover_data=["Country", "PM2.5 AQI Value"],
    color_discrete_map={
        'Good': 'green', 'Moderate': 'yellow', 'Unhealthy': 'orange', 
        'Unhealthy for Sensitive Groups': 'darkorange', 'Very Unhealthy': 'red', 'Hazardous': 'purple'
    },
    zoom=1, 
    height=600,
    mapbox_style="carto-positron"
)
st.plotly_chart(fig_map, use_container_width=True)

# Row 3: Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Average AQI by Country")
    country_avg = filtered_df.groupby('Country')['AQI Value'].mean().reset_index().sort_values('AQI Value', ascending=False)
    fig_bar = px.bar(country_avg, x='Country', y='AQI Value', color='AQI Value', color_continuous_scale='Reds')
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("🧪 Pollutant Composition")
    # Calculate main offender for the filtered set
    pollutants = ['CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']
    main_pollutants = filtered_df[pollutants].mean().sort_values(ascending=False).reset_index()
    main_pollutants.columns = ['Pollutant', 'Mean Value']
    fig_pie = px.pie(main_pollutants, values='Mean Value', names='Pollutant', hole=0.4, color_discrete_sequence=px.colors.sequential.Viridis)
    st.plotly_chart(fig_pie, use_container_width=True)

# Data Table
with st.expander("View Raw Filtered Data"):
    st.dataframe(filtered_df)