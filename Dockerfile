# ============================================================
# Production Dockerfile — Fast build, pre-baked models, non-root
# ============================================================

# Stage 1: Builder
FROM python:3.13-slim AS builder

# Install build dependencies + curl for uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install uv (much faster than pip)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install CPU-only torch first (prevents pulling huge CUDA version)
RUN uv pip install --system torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install the rest of the dependencies
RUN uv pip install --system --no-cache -r requirements.txt

# Pre-download heavy models during build (this is the key for fast startup)
RUN python -c 'import os; os.environ["HF_HOME"] = "/root/.hf_cache"; os.environ["TRANSFORMERS_CACHE"] = "/root/.hf_cache"; from transformers import MarianTokenizer, MarianMTModel; from detoxify import Detoxify; print("Downloading Helsinki-NLP/opus-mt-vi-en..."); MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-vi-en"); MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-vi-en"); print("Downloading detoxify original..."); Detoxify("original"); print("All models pre-downloaded successfully.");'

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

# Create non-root user
RUN groupadd --system agent && \
    useradd --system --gid agent --create-home --shell /bin/false agent

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy pre-downloaded HF cache
COPY --from=builder --chown=agent:agent /root/.hf_cache /app/.hf_cache

# Copy application code
COPY --chown=agent:agent defense/ ./defense/
COPY --chown=agent:agent main.py app.py ./

# Set correct ownership and environment
RUN chown -R agent:agent /app

USER agent

ENV PATH=/usr/local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/agent

# Hugging Face cache inside container
ENV HF_HOME=/app/.hf_cache
ENV TRANSFORMERS_CACHE=/app/.hf_cache
ENV HF_HUB_CACHE=/app/.hf_cache

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]