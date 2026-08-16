FROM python:3.12-slim

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Instalar dependências de compilação (se necessárias para psycopg2 ou pymupdf)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto para dentro do container
COPY . .

# Comando padrão (usando uvicorn para o servidor rodar e escutar a porta do Railway)
CMD uvicorn core.api:app --host 0.0.0.0 --port ${PORT:-8000}
