import streamlit as st
import pandas as pd
import plotly.express as px

# Set wide layout
st.set_page_config(layout="wide")

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv("cleaned_data_fixed.csv")

df = load_data()

# Sidebar - Filters
st.sidebar.header("Filter Listings")

location = st.sidebar.multiselect("Select Location", sorted(df['location'].dropna().unique()))
property_type = st.sidebar.multiselect("Property Type", sorted(df['property_type'].dropna().unique()))
furnished = st.sidebar.multiselect("Furnishing", sorted(df['furnished'].dropna().unique()))

min_rent = int(df['monthly_rent'].min())
max_rent = int(df['monthly_rent'].max())
rent_range = st.sidebar.slider("Monthly Rent (RM)", min_rent, max_rent, (min_rent, max_rent))

near_ktm = st.sidebar.checkbox("Only show listings near KTM/LRT")

# Apply filters
filtered = df[
    (df['monthly_rent'] >= rent_range[0]) & 
    (df['monthly_rent'] <= rent_range[1])
]

if location:
    filtered = filtered[filtered['location'].isin(location)]
if property_type:
    filtered = filtered[filtered['property_type'].isin(property_type)]
if furnished:
    filtered = filtered[filtered['furnished'].isin(furnished)]
if near_ktm:
    filtered = filtered[filtered['near ktm/lrt'] == True]

# Title
st.title("Rental Apartment Dashboard")
st.write("This interactive dashboard visualises apartment rental listings in Kuala Lumpur and Selangor.")
st.markdown(f"Showing **{len(filtered)}** listings after filtering.")

# Custom padding
st.markdown("<style>section.main > div { padding-left: 1rem; padding-right: 1rem; }</style>", unsafe_allow_html=True)

# --- Row 1: Rental Overview (2) + Top Locations (1) ---
row1_left, row1_right = st.columns([2, 1])

with row1_left:
    st.markdown("#### Rental Price Overview")

    avg_rent = filtered['monthly_rent'].mean()
    max_rent = filtered['monthly_rent'].max()
    min_rent = filtered['monthly_rent'].min()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""<div style="background-color:#f9f9f9; padding:20px; border-radius:10px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.1); text-align:center;">
            <h5 style="color:#444;">Average Rent</h5>
            <h2 style="color:#2e7d32;">RM {avg_rent:.0f}</h2>
            <p style="color:#2e7d32; margin:0;">↑ Stable</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div style="background-color:#f9f9f9; padding:20px; border-radius:10px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.1); text-align:center;">
            <h5 style="color:#444;">Max Rent</h5>
            <h2 style="color:#d32f2f;">RM {max_rent:.0f}</h2>
            <p style="color:#d32f2f; margin:0;">↑ High</p>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""<div style="background-color:#f9f9f9; padding:20px; border-radius:10px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.1); text-align:center;">
            <h5 style="color:#444;">Min Rent</h5>
            <h2 style="color:#0288d1;">RM {min_rent:.0f}</h2>
            <p style="color:#0288d1; margin:0;">↓ Low</p>
        </div>""", unsafe_allow_html=True)

with row1_right:
    st.markdown("#### Top Locations")
    top_locations_df = (
        filtered['location']
        .value_counts()
        .reset_index()
    )
    top_locations_df.columns = ['location', 'listing_count']

    st.dataframe(
        top_locations_df,
        column_order=("location", "listing_count"),
        hide_index=True,
        use_container_width=True,
        column_config={
            "location": st.column_config.TextColumn("Location"),
            "listing_count": st.column_config.ProgressColumn(
                "Listings",
                format="%d",
                min_value=0,
                max_value=int(top_locations_df["listing_count"].max())
            )
        }
    )

# --- Row 2: Rent by Furnishing (1) + Property Type (1) ---
row2_left, row2_right = st.columns(2)

with row2_left:
    st.markdown("#### Rent by Furnishing")
    fig_hist = px.histogram(filtered, x="monthly_rent", nbins=30, color="furnished")
    st.plotly_chart(fig_hist, use_container_width=True)

with row2_right:
    st.markdown("#### Rent by Property Type")
    fig_box = px.box(filtered, x='property_type', y='monthly_rent', color='property_type')
    st.plotly_chart(fig_box, use_container_width=True)

# --- Row 3: Raw Data (2) + About (1) ---
row3_left, row3_right = st.columns([2, 1])

with row3_left:
    with st.expander("View Raw Data"):
        st.dataframe(filtered.drop(columns=['ads_id','completion_year']), use_container_width=True)

with row3_right:
    st.markdown("### About This Dashboard")
    st.markdown("""
    **Features**:
    - Filters by location, furnishing status, property type, price range, and proximity to KTM/LRT
    - Provides visual insights into rental distribution, furnishing trends, and property types
    - Assists renters and researchers in identifying affordable housing areas
    - Developed as a group project for the Principles of Data Management(ICT550) course under Ts. Dr. Norziana Yahya, UiTM Perlis         

    """)
