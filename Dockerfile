FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libmagic1 \
        libpq-dev \
        libreoffice \
        libreoffice-java-common \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install "Flask<2.3" "Werkzeug<2.3" "SQLAlchemy<1.4" \
    && pip install -r requirements.txt \
    && pip install requests PyJWT clean-text sqlalchemy-paginator torch

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
