FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set the entrypoint to run the script
ENTRYPOINT ["python", "bdm-auto-couponer.py"]