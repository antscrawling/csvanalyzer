# Use a standard Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only the files needed to run main.py
COPY src/ ./src/
COPY requirements.txt ./

# Install dependencies directly using pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir duckdb

# Set environment variables
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# Run the main application
CMD ["python", "src/main.py"]