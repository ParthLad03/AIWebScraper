# Use Python 3.11 (instead of 3.13 to avoid compatibility issues)
FROM python:3.11-slim

# Install Rust toolchain needed by pydantic-core via maturin
RUN apt-get update && apt-get install -y curl build-essential \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && export PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt ./

# Install Python dependencies
RUN /bin/bash -c "source $HOME/.cargo/env && pip install --no-cache-dir -r requirements.txt"

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]
