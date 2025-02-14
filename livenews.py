import asyncio
import logging
import psycopg2
import argparse
import time
import os
from datetime import datetime
from typing import Union, Dict, List
from dotenv import load_dotenv
from alpaca.data import NewsClient
from alpaca.data.live import NewsDataStream
from alpaca.data.requests import NewsRequest
from alpaca.data.models.news import News
from pydantic import BaseModel
from urllib3.exceptions import MaxRetryError, NewConnectionError
from requests.exceptions import ConnectionError

#----------------------------------------------------------------
#
#  Purpose:  Get Real time News stories from Alpaca and
#            insert them into postgres timescale db
#
#            set up a .env file with these parms:
#            ALPACA_API_KEY=your_api_key_here
#            ALPACA_SECRET_KEY=your_secret_key_here
#            POSTGRES_DB=your_db_name
#            POSTGRES_USER=your_db_user
#            POSTGRES_PASSWORD=your_db_password
#            POSTGRES_HOST=your_db_host
#            POSTGRES_PORT=your_db_port
#
#----------------------------------------------------------------
# Enable logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Command-line argument parser
parser = argparse.ArgumentParser(description="Alpaca News Streaming with PostgreSQL")
parser.add_argument("--api_key", help="Alpaca API Key", default=os.getenv("ALPACA_API_KEY"))
parser.add_argument("--secret_key", help="Alpaca Secret Key", default=os.getenv("ALPACA_SECRET_KEY"))
args = parser.parse_args()

API_KEY = args.api_key
SECRET_KEY = args.secret_key

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT")
    )

# Define Pydantic model for news updates
class NewsUpdate(BaseModel):
    id: int
    headline: str
    summary: str
    author: str
    content: str
    symbols: List[str]
    source: str
    url: str
    created_at: datetime
    updated_at: datetime

async def news_handler(news: Union[News, Dict]) -> None:
    """Callback function to handle incoming news data and insert it into PostgreSQL."""
    print("Received News Update:")
    
    if isinstance(news, News):
        try:
            # Convert News object to JSON and validate with Pydantic
            json_str = news.model_dump_json()
            news_obj = NewsUpdate.model_validate_json(json_str)

            # Insert into PostgreSQL
            conn = get_db_connection()
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO news_updates (headline, summary, author, content, symbols, source, url, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                news_obj.headline,
                news_obj.summary,
                news_obj.author,
                news_obj.content,
                news_obj.symbols,
                news_obj.source,
                news_obj.url,
                news_obj.created_at,
                news_obj.updated_at
            ))

            conn.commit()
            cursor.close()
            conn.close()
            print("News update inserted into PostgreSQL.")

        except Exception as e:
            print(f"Error inserting into database: {e}")
    else:
        print(news)  # If raw data is returned

async def main():
    retry_attempts = 5
    attempt = 0

    while attempt < retry_attempts:
        try:
            # Verify API connection with a simple news request.
            news_client = NewsClient(api_key=API_KEY, secret_key=SECRET_KEY)
            request_params = NewsRequest(start=datetime.now().date())

            print(f"Testing API connection... (Attempt {attempt + 1}/{retry_attempts})")

            try:
                news = news_client.get_news(request_params)
                print("API connection successful!")
                print("Sample news received.")
                break  # Exit retry loop
            
            except (ConnectionError, MaxRetryError, NewConnectionError) as conn_err:
                print(f"Network error: {conn_err}")
                print("Possible causes: No internet, API down, DNS resolution failure.")
                attempt += 1
                if attempt < retry_attempts:
                    print(f"Retrying in {5 * attempt} seconds...")
                    time.sleep(5 * attempt)  # Exponential backoff
                else:
                    print("Max retry attempts reached. Exiting.")
                    return

        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("\nPlease verify your API credentials and network.")
            return

    # Initialize the news stream
    stream = NewsDataStream(api_key=API_KEY, secret_key=SECRET_KEY)

    # Subscribe to news updates for all symbols.
    print("Subscribe to news updates for all symbols")
    stream.subscribe_news(news_handler, "*")

    print("\nStarting news stream...")
    await stream._run_forever()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nStream terminated by user")
