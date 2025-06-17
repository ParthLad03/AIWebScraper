FROM python:3.11-slim

# Install Rust and system dependencies for pydantic-core
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    pkg-config \
    git \
    && apt-get clean

# Install Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY backend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app from backend/main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
