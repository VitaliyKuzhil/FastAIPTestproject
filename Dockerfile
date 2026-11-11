# syntax=docker/dockerfile:1

# Set root image
FROM python:3.12-slim

# Set image metadata
LABEL authors="Vitalii Kuzhil"
LABEL version="1.0"

# Set work directory for container
WORKDIR /app

# Set settings environments
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only requirements to docker cache
COPY requirements.txt .

# Run command into container (Install dependencies)
RUN pip install --no-cache-dir -r requirements.txt

# Copy project (. - current position) into WORKDIR
COPY . .

# Expose application port
EXPOSE 8000

# Run FastAPI application with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]