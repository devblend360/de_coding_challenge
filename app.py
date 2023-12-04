import streamlit as st
import pandas as pd
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from matplotlib import pyplot as plt
# # snowflake connection 
# account = "db68116.ap-south-1.aws",
# user = "DEVBLEND360", 
# password = "Dev@942065",
# database = "CODINGCHALLENGE",
# schema = "PUBLIC",
# warehouse = "COMPUTE_WH"
# table_name = "BOOKS"

# Snowflake connection
engine = create_engine(URL(
    account = "db68116.ap-south-1.aws",
    user = "DEVBLEND360", 
    password = "Dev@942065",
    database = "CODINGCHALLENGE",
    schema = "PUBLIC",
    warehouse = "COMPUTE_WH"
    ))


# Load data
def load_data():
    query = "SELECT * FROM books"
    books_df = pd.read_sql(query, engine)
    return books_df


books_df = load_data()


st.title("Book Analysis Dashboard")

st.sidebar.header("Options:")
rating_filter = st.sidebar.multiselect(
    "Select the Ratings:",
    options=books_df["rating"].unique(),
    default=books_df["rating"].unique()  
)

df_selection = books_df.query(
    "rating == @rating_filter"  
)

# st.dataframe(df_selection)

# Charts
ratings_count = df_selection['rating'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(ratings_count, labels=ratings_count.index, autopct="%1.1f%%", shadow=True)
ax1.axis("equal")  
st.write("""#### Ratings Percentage""")
st.pyplot(fig1)



# Total books metric
total_books = books_df.shape[0]  
st.metric("Total Books", str(total_books))


# Filters
rating_filter = st.slider("Mininum Rating", 1, 5, 1)  
availability_filter = st.selectbox("Availability Filter", ["All"]+list(books_df["availability"].unique()))

# Apply filters
filtered_df = books_df[books_df["rating"] >= rating_filter] 
if availability_filter != "All":
    filtered_df = filtered_df[filtered_df["availability"]==availability_filter]
    
# Show dataframe table    
st.dataframe(filtered_df)
