FROM python:3.11-slim

WORKDIR /app

# Bağımlılıkları kopyala
COPY requirements.txt .

# Python bağımlılıklarını yükle
RUN pip install --no-cache-dir -r requirements.txt

# spaCy modelini yükle
RUN python -m spacy download en_core_web_sm

# Uygulama kodlarını kopyala
COPY . .

# Web sunucusunu çalıştır
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 