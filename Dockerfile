# Dockerfile

# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /code

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
