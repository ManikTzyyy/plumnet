# Gunakan base image Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies OS untuk paramiko/netmiko
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy dan install dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh project ke container
COPY . .

# Expose port Django
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
