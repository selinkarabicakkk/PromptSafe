# PromptSafe

PromptSafe, şirket çalışanlarının bulut tabanlı yapay zeka modellerine (ChatGPT, Claude, Gemini vb.) hassas verileri göndermesini engelleyen bir güvenlik middleware servisidir.

## Özellikler

- Regex tabanlı hassas veri tespiti ve maskeleme
- NER (Named Entity Recognition) ile kişisel veri tespiti
- OpenAI, Anthropic ve Google API entegrasyonları
- FastAPI tabanlı asenkron servis yapısı
- Docker desteği ile kolay dağıtım

## Kurulum

```bash
# Sanal ortam oluşturma
python -m venv venv

# Sanal ortamı aktifleştirme (Windows)
venv\Scripts\activate

# Sanal ortamı aktifleştirme (Linux/MacOS)
source venv/bin/activate

# Gereksinimleri yükleme
pip install -r requirements.txt

# spaCy modelini indirme
python -m spacy download en_core_web_sm
```

## Kullanım

```bash
# Geliştirme sunucusunu başlatma
uvicorn app.main:app --reload
```

Servis varsayılan olarak http://localhost:8000 adresinde çalışacaktır.
API dokümantasyonuna http://localhost:8000/docs adresinden erişebilirsiniz.
