# Use official Python image as base
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app folder into /app/app
COPY app/ app/

# Run the FastAPI app from inside app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]