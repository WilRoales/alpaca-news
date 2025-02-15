# Alpaca News App

This project collects and stores real-time news updates from Alpaca in a PostgreSQL database.

## Getting Started
git clone https://github.com/WilRoales/alpaca.git
cd alpaca🚀 Alpaca News Service Setup Guide
# Step 1: Create a Free Alpaca Paper Trading Account
To access live market data and news, you'll need an Alpaca API key.
Sign up for a free paper trading account at Alpaca.
Once logged in, navigate to API Keys & OAuth → Generate API Key.
Save your API Key and Secret Key (you'll need these in Step 2).
# Step 2: Clone the Repository

git clone https://github.com/WilRoales/alpaca-news.git
cd alpaca-news
# Step 3: Create a .env File
Copy .env.example to .env and update it with your Alpaca API keys and database credentials.

cp .env.example .env
nano .env  # Edit and replace API_KEY & SECRET_KEY
# Step 4: Start PostgreSQL with TimescaleDB
Run the PostgreSQL container with TimescaleDB support:

docker run -d --name alpaca-db \
  -p 5432:5432 \
  -e POSTGRES_USER=alpaca \
  -e POSTGRES_PASSWORD=alpaca_pass \
  -e POSTGRES_DB=alpaca_news \
  timescale/timescaledb:latest-pg15
  
# Check if it's running:

docker ps

# Step 5: Start up Alpaca News Script

docker run -d --name alpaca-news \
  --env-file .env \
  --network="host" \
  william61/alpaca-news:latest
  
# Step 6: Verify It’s Working

Check logs for news streaming:

docker logs -f alpaca-news

# Step 8: (Optional) Restart Services
If needed:

docker restart alpaca-db
docker restart alpaca-news

