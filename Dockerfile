FROM python:3.10-slim

# Instalar dependencias del sistema que Prophet necesita
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libgomp1 \
    libatlas-base-dev \
    liblapack-dev \
    libstdc++6 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
