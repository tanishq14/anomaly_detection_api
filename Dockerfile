# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for some ML/Image processing libraries)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# Install gdown for Google Drive downloading
RUN pip install gdown

# Copy the rest of the backend code
COPY . .

# Expose Hugging Face's required port
EXPOSE 7860

# 1. Download the models from Google Drive
# 2. Start the Flask app
CMD python download_models.py && python app.py