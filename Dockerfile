FROM python:3.11-slim

WORKDIR /app

RUN mkdir config
RUN mkdir cache

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY bdm-auto-couponer.py .

# Set the entrypoint to run the script
ENTRYPOINT ["python", "bdm-auto-couponer.py"]