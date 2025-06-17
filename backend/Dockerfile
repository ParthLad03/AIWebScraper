# Use Python 3.11 (instead of 3.13 to avoid compatibility issues)
FROM python:3.11-slim

# Install system dependencies including ones needed by browsers
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    wget \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxkbcommon0 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    && apt-get clean

# Install Rust (required by some Python packages)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies
RUN /bin/bash -c "source $HOME/.cargo/env && pip install --no-cache-dir -r requirements.txt"

# ⬇️ Add this line to install browsers for Playwright
RUN playwright install --with-deps

# Copy your app
COPY . .

# Expose app port
EXPOSE 8000

# Start the app
CMD ["python", "main.py"]
