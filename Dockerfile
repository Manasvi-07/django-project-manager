# Use official Python image
FROM python:3.13-slim

# Create a non-root user
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Default command (overridden in docker-compose)
CMD ["gunicorn", "demo_project.wsgi:application", "--bind", "0.0.0.0:8000"]