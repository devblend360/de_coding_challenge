import streamlit as st
import pandas as pd
from snowflake import connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from forex_python.converter import CurrencyRates
import humanize

# Snowflake connection
engine = create_engine(URL(
    account="db68116.ap-south-1.aws",
    user="DEVBLEND360",
    password="Dev@942065",
    database="CODINGCHALLENGE",
    schema="PUBLIC",
    warehouse="COMPUTE_WH"
))

# Load data
def load_data():
    query = "SELECT * FROM books"
    books_df = pd.read_sql(query, engine)
    return books_df

def convert_to_currency(price_in_dollars, exchange_rate):
    return price_in_dollars * exchange_rate

# Fetch real-time exchange rate
def get_exchange_rate(target_currency):
    currency_rates = CurrencyRates()
    return currency_rates.get_rate('USD', target_currency)

books_df = load_data()

st.title("Book Analysis Dashboard")

# Sidebar filters
st.sidebar.header("Filters:")
# Use a multiselect dropdown for selecting ratings
rating_filter = st.sidebar.multiselect(
    "Select Ratings:",
    options=list(books_df["rating"].unique()),
    default=list(books_df["rating"].unique())
)

availability_filter = st.sidebar.selectbox(
    "Select Availability:",
    ["All"] + list(books_df["availability"].unique())
)

# Currency selection
selected_currency = st.sidebar.radio("Select Currency:", ["USD", "INR"], index=0)

# Apply filters
filtered_df = books_df[(books_df["rating"].isin(rating_filter)) & 
                        ((availability_filter == "All") | (books_df["availability"] == availability_filter))]

# Fetch real-time exchange rate
exchange_rate = get_exchange_rate("INR") if selected_currency == "INR" else 1.0

# Convert prices to selected currency
filtered_df['price_in_selected_currency'] = convert_to_currency(filtered_df['price'], exchange_rate)

# Total books KPI
total_books = filtered_df.shape[0]
st.sidebar.metric("Total Books", total_books)

# Average Price KPI
avg_price = filtered_df['price_in_selected_currency'].mean()
st.sidebar.metric(f"Average Price ({selected_currency})", f"{selected_currency} {avg_price:.2f}")

# Total Revenue KPI
total_revenue = (filtered_df['price'] * total_books).sum()
total_revenue_in_selected_currency = convert_to_currency(total_revenue, exchange_rate)
formatted_total_revenue = humanize.intword(total_revenue_in_selected_currency)  # Format large numbers
st.sidebar.metric(f"Total Revenue ({selected_currency})", f"{selected_currency} {formatted_total_revenue}")

# Layout in columns
col1, col2 = st.columns(2)

# Ratings Percentage Pie Chart
with col1:
    st.subheader("Ratings Percentage")
    ratings_count = filtered_df['rating'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(ratings_count, labels=ratings_count.index, autopct="%1.1f%%", shadow=True)
    ax1.axis("equal")
    st.pyplot(fig1)

# Price Distribution Histogram
with col2:
    st.subheader("Price Distribution")
    fig2, ax2 = plt.subplots()
    filtered_df['price_in_selected_currency'].plot(kind='hist', bins=20, edgecolor='black', ax=ax2)
    ax2.set_xlabel(f"Price ({selected_currency})")
    ax2.set_ylabel("Frequency")
    st.pyplot(fig2)

# Display Filtered DataFrame Table
st.subheader("Filtered Book Data")
st.dataframe(filtered_df[['title', 'price_in_selected_currency', 'rating', 'availability']])

# Show the Streamlit app
st.sidebar.text("Dashboard Filters Applied:")
st.sidebar.text(f"Selected Ratings: {rating_filter}")
st.sidebar.text(f"Selected Availability: {availability_filter}")
st.sidebar.text(f"Selected Currency: {selected_currency}")
