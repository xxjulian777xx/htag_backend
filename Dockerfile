FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Zona horaria de México
ENV TZ=America/Mexico_City

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tzdata \
        tesseract-ocr \
        tesseract-ocr-spa \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000