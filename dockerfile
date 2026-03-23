FROM python:3.11-slim

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

# Dependências do sistema
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Atualizar pip
RUN python -m pip install --upgrade pip

# Instalar numpy fixo compatível com spacy<3.6
RUN pip install "numpy==1.26.4"

# Instalar dependências restantes
RUN pip install -r requirements.txt

# Copiar código
COPY . .

# Baixar modelo pt compatível
RUN python -m spacy download pt_core_news_sm-3.5.0

# Expor porta FastAPI
EXPOSE 8000

# Rodar FastAPI com hot-reload
CMD ["uvicorn", "lucia:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]