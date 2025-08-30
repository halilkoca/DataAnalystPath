import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# read data
df = pd.read_csv("data/real_estate_texas_500_2024.csv")

# out of Land ve Farm
filtered_df = df[~df['type'].isin(["land", "farm"])]

# removes beds NaN
filtered_df = filtered_df[filtered_df['beds'].notna()]

# --- Streamlit Dashboard ---
st.title("🏡 Texas Housing Market Analysis")

# 🔹 Filters (sidebar)
st.sidebar.header("Filter")

# Property Type filter
type_options = sorted(filtered_df['type'].unique())
type_filter = st.sidebar.multiselect("Property Type:", options=type_options, default=type_options)

# Bedrooms filter
bed_options = sorted(filtered_df['beds'].unique())
bed_filter = st.sidebar.multiselect("Bedrooms:", options=bed_options, default=bed_options)

# Bath filter
bath_options = sorted(filtered_df['baths'].dropna().unique())
bath_filter = st.sidebar.multiselect("Bathrooms:", options=bath_options, default=bath_options)

# Price filter
min_price, max_price = int(filtered_df['listPrice'].min()), int(filtered_df['listPrice'].max())
price_filter = st.sidebar.slider("Price range:", min_price, max_price, (min_price, max_price))

min_sqft, max_sqft = int(filtered_df['sqft'].min()), int(filtered_df['sqft'].max())
sqft_filter = st.sidebar.slider("Square Footage Range:", min_sqft, max_sqft, (min_sqft, max_sqft))

# Apply filters
df_filtered = filtered_df[
    (filtered_df['type'].isin(type_filter)) &
    (filtered_df['beds'].isin(bed_filter)) &
    (filtered_df['baths'].isin(bath_filter)) &
    (filtered_df['listPrice'].between(price_filter[0], price_filter[1])) &
    (filtered_df['sqft'].between(sqft_filter[0], sqft_filter[1]))
]


# Common Statistics
st.subheader("Common Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Housing", len(df_filtered))
col2.metric("Average Price", f"${df_filtered['listPrice'].mean():,.0f}")
col3.metric("Average Bedrooms", round(df_filtered['beds'].mean(), 1))

# Average Price By Number Of Bedroom
st.subheader("Average Price By Number Of Bedroom")
avg_price_by_beds = df_filtered.groupby("beds")["listPrice"].mean().reset_index()
fig1 = px.bar(avg_price_by_beds, x="beds", y="listPrice",
              labels={"beds": "Bedrooms", "price": "Average Price"},
              title="Average Price By Number Of Bedroom")
st.plotly_chart(fig1)

# Maps (if latitude, longitude)
if "lat" in df_filtered.columns and "long" in df_filtered.columns:
    st.subheader("Texas Map - Price")
    fig2 = px.scatter_mapbox(df_filtered,
                             lat="lat",
                             lon="long",
                             size="listPrice",
                             color="listPrice",
                             hover_data=["listPrice", "beds", "sqft"],
                             color_continuous_scale=px.colors.cyclical.IceFire,
                             size_max=15,
                             zoom=4,
                             mapbox_style="open-street-map")
    st.plotly_chart(fig2)

# Price Distribution Histogram
# where most homes are priced
st.subheader('Price Distribution')
fig3 = px.histogram(df_filtered,
                    x='listPrice',
                    nbins=50,
                    title='The histogram shows us in which ranges prices are concentrated.',
                    labels={'listPrice': 'Price ($)'})
st.plotly_chart(fig3)


# Scatter Plot: Sqft vs Price
# This is a must-have for investors 📈 because it reveals the relationship between home size (sqft) and price.
# Large but cheap homes → potential investment opportunities.
# Small but overpriced homes → possible overvalued risks.
if 'sqft' in df_filtered.columns:
    st.subheader('Square Footage vs Price')
    fig4 = px.scatter(df_filtered,
                      x='sqft',
                      y='listPrice',
                      color='beds',
                      hover_data=['baths', 'type'],
                      title='Highlights good vs bad investment opportunities')
    st.plotly_chart(fig4)
    
# helps investors compare value across houses, not just absolute price
df_filtered['price_per_sqft'] = df_filtered['listPrice'] / df_filtered['sqft']
fig5 = px.histogram(df_filtered, x='price_per_sqft', nbins=50, title='Price per Square Foot Distribution')
st.plotly_chart(fig5)


# Correlation Heatmap
# Show correlations between price, beds, baths, sqft.
# Great for data analysis insight.
st.subheader("Correlation Heatmap")
corr = df_filtered[['listPrice','beds','baths','sqft']].corr()
fig6, ax = plt.subplots()
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig6)

# Top 10 Most Expensive Homes
st.subheader("Top 10 Most Expensive Homes")
top10 = df_filtered.nlargest(10, 'listPrice')[['type','beds','baths','sqft','listPrice']]
st.table(top10)
