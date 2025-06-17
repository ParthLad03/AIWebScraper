# Use Python 3.11 (not 3.13 for compatibility)
FROM python:3.11-slim

# Install Rust toolchain (for pydantic-core compiled dependencies)
RUN apt-get update && apt-get install -y curl build-essential \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && echo 'source $HOME/.cargo/env' >> ~/.bashrc

# Set working directory
WORKDIR /app

# Copy dependencies first (for caching)
COPY requirements.txt .

# Source Rust env & install Python dependencies
RUN /bin/bash -c "source $HOME/.cargo/env && pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt"

# Copy rest of the app
COPY . .

# Expose app port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
