FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements / configuration
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi>=0.115.0 \
    "uvicorn[standard]>=0.30.0" \
    chromadb>=0.5.0 \
    sentence-transformers>=3.0.0 \
    httpx>=0.27.0 \
    google-genai>=1.0.0 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0 \
    python-dotenv>=1.0.0 \
    python-multipart>=0.0.9 \
    aiosqlite>=0.20.0 \
    beautifulsoup4>=4.12.0 \
    markdownify>=0.13.0

# Copy application source
COPY . .

# Preload seed data on build
RUN python -m data.seed_loader || true

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
