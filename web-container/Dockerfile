# web-container/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories if they don't exist
RUN mkdir -p static/css static/js templates

# Expose port for the Flask app
EXPOSE 3000

# Run the Flask app
CMD ["python", "app.py"]
