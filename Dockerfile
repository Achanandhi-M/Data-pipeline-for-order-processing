# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the Avro schema and the Python consumer code
COPY order_schema.avsc consumer.py .

# Run the Python consumer
CMD ["python", "consumer.py"]
