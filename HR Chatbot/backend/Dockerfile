FROM python:3.11-slim

# Set environment variable to avoid Unicode issues
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

# Copy the requirements file first for better caching
COPY requirements.txt /app/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

EXPOSE 8000

ENV FLASK_APP=run.py

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "run:app"]