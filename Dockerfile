# Use official Python base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first (for caching layers)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the script
CMD ["python", "livenews.py"]
