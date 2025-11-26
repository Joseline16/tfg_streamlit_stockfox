FROM python:3.10-slim

# Dependencias mínimas necesarias para numpy, scipy, statsmodels y psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir numpy
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
