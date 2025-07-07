import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Load data
df = pd.read_csv('data/zomato_swiggy_full_dataset.csv')
df["Extra Charges"] = df["Final Price"] - df["Base Price"]

st.title("Zomato vs Swiggy Price Analytics Dashboard")

#  SIDEBAR 
st.sidebar.header("Filters")
city = st.sidebar.selectbox("Select City", df['City'].unique())
dish = st.sidebar.selectbox("Select Dish", df['Dish'].unique())

min_price, max_price = st.sidebar.slider("Select Final Price Range", 0, 500, (100, 300))
filtered_price = df[(df["Final Price"] >= min_price) & (df["Final Price"] <= max_price)]

# MAIN VIEW 
filtered = df[(df['City'] == city) & (df['Dish'] == dish)].copy()

st.subheader(f"Price Comparison for '{dish}' in {city}")

# Price table with highlight
highlight = filtered[["App", "Base Price", "Delivery Fee", "Packaging Fee", "Platform Fee", "Final Price", "Extra Charges"]]
st.dataframe(highlight.style.highlight_min(subset=["Final Price"], color="lightgreen"))

# Final price bar chart
st.subheader("Final Price by App")
st.bar_chart(filtered.set_index("App")["Final Price"])

# Emoji tag (cheap vs costly)
filtered.loc[:, "Tag"] = filtered["Final Price"].apply(
    lambda x: "✅ Cheaper" if x == filtered["Final Price"].min() else "💸 Costly"
)
st.write("App Tags Based on Final Price:")
st.dataframe(filtered[["App", "Final Price", "Tag"]])

# Pie chart: fee breakdown
st.subheader("Charges Breakdown (Pie Chart)")
selected_app = st.selectbox("Select App", filtered["App"].unique())

app_data = filtered[filtered["App"] == selected_app].iloc[0]
labels = ['Delivery Fee', 'Packaging Fee', 'Platform Fee']
sizes = [app_data['Delivery Fee'], app_data['Packaging Fee'], app_data['Platform Fee']]

fig1, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig1)

# Radar chart (Plotly)
st.subheader("Cost Breakdown Radar Chart")
radar_df = filtered[["App", "Base Price", "Delivery Fee", "Packaging Fee", "Platform Fee", "Final Price"]]

fig2 = go.Figure()
for _, row in radar_df.iterrows():
    fig2.add_trace(go.Scatterpolar(
        r=row[1:].values,
        theta=radar_df.columns[1:],
        fill='toself',
        name=row["App"]
    ))
fig2.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
st.plotly_chart(fig2)

# Average final price across cities
st.subheader("Average Final Price Across Cities")
avg_city = df.groupby(['City', 'App'])['Final Price'].mean().unstack()
st.bar_chart(avg_city)

# App with lowest avg per city
st.subheader("App with Lowest Avg Price in Each City")
city_cheapest = df.groupby(['City', 'App'])['Final Price'].mean().reset_index()
cheapest_rows = city_cheapest.loc[city_cheapest.groupby('City')['Final Price'].idxmin()]
st.dataframe(cheapest_rows)

# Overall cheapest app
st.subheader("Cheapest App Overall (Across All Cities & Dishes)")
avg_prices = df.groupby("App")["Final Price"].mean().sort_values()
st.write(f"`{avg_prices.index[0]}` is the overall cheapest on average (₹{avg_prices.values[0]:.2f})")

# CSV Download
st.download_button(
    label="Download Filtered Data",
    data=filtered.to_csv(index=False),
    file_name=f"{city}_{dish}_price_comparison.csv",
    mime='text/csv'
)

# Filtered by price range
st.subheader("Records Matching Final Price Range")
st.dataframe(filtered_price.head(10))

