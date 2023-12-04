import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://books.toscrape.com/"

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

books = []

for book in soup.find_all('article', class_="product_pod"):
    title = book.find('h3').find('a')['title']
    rating = book.find('p')['class'][1]
    price = book.find(class_='price_color').text[2:]  
    availability = "In stock" if book.find(class_='instock availability').text.strip()=="In stock" else "Out of stock"
    
    book_data = {
        "title": title,
        "rating": rating, 
        "price": price,
        "availability": availability
    }
    
    books.append(book_data)
    
df = pd.DataFrame(books)
df['title'] = df['title'].astype('str')
df['rating'] = df['rating'].astype('str')
df['price'] = df['price'].astype('float')
df['availability'] = df['availability'].astype('str')
# Dictionary mapping rating words to numbers 
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}
# Apply mapping to replace text with numbers
df["rating"] = df["rating"].map(rating_map)
# Step 2: Data Storage with Snowflake
import pandas as pd
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine  
import pandas as pd
import snowflake.connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine


# Snowflake connection
engine = create_engine(URL(
    account = "db68116.ap-south-1.aws",
    user = "DEVBLEND360", 
    password = "Dev@942065",
    database = "CODINGCHALLENGE",
    schema = "PUBLIC",
    warehouse = "COMPUTE_WH"
    ))

# Append dataframe to Snowflake table
df.to_sql('books', engine, if_exists='replace', index=False)

print("Books data loaded to Snowflake")
