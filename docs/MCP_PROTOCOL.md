# Model-Context-Protocol (MCP) Dokümantasyonu

Model-Context-Protocol (MCP), farklı LLM (Büyük Dil Modelleri) sağlayıcıları arasında standart bir iletişim protokolüdür. Bu dokümantasyon, PromptSafe'in MCP desteğini ve kullanımını açıklar.

## İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [MCP İstek Formatı](#mcp-i̇stek-formatı)
3. [MCP Yanıt Formatı](#mcp-yanıt-formatı)
4. [Desteklenen Sağlayıcılar](#desteklenen-sağlayıcılar)
5. [Örnekler](#örnekler)

## Genel Bakış

Model-Context-Protocol (MCP), farklı LLM sağlayıcıları (OpenAI, Anthropic, Google vb.) için ortak bir API formatı sağlar. Bu protokol sayesinde, uygulamalar tek bir API formatını kullanarak farklı LLM sağlayıcılarına istek gönderebilir.

PromptSafe, MCP formatındaki istekleri alır, hassas verileri filtreler ve uygun LLM sağlayıcısına yönlendirir. Sağlayıcıdan gelen yanıtı da filtreleyerek MCP formatında döndürür.

## MCP İstek Formatı

MCP istek formatı, aşağıdaki alanları içerir:

```json
{
  "messages": [
    { "role": "system", "content": "Sen yardımcı bir asistansın." },
    { "role": "user", "content": "Merhaba, nasılsın?" },
    { "role": "assistant", "content": "Size nasıl yardımcı olabilirim?" },
    { "role": "user", "content": "Hava durumu nasıl?" }
  ],
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "temperature": 0.7,
  "max_tokens": 1024,
  "additional_params": {
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
  }
}
```

### Zorunlu Alanlar

- `messages`: Konuşma geçmişini içeren mesaj dizisi. Her mesaj, `role` ve `content` alanlarına sahip olmalıdır.
  - `role`: Mesajın rolü. Değerler: `system`, `user`, `assistant`.
  - `content`: Mesajın içeriği.
- `provider`: LLM sağlayıcısı. Değerler: `openai`, `anthropic`, `google`.

### İsteğe Bağlı Alanlar

- `model`: Kullanılacak model adı. Belirtilmezse, sağlayıcının varsayılan modeli kullanılır.
- `temperature`: Yanıtın yaratıcılık seviyesi (0.0-1.0). Varsayılan: 0.7.
- `max_tokens`: Yanıtın maksimum token sayısı. Varsayılan: 1024.
- `additional_params`: Sağlayıcıya özel ek parametreler.

## MCP Yanıt Formatı

MCP yanıt formatı, istek formatına benzer ancak asistan yanıtını ve PromptSafe metadata'sını içerir:

```json
{
  "messages": [
    { "role": "system", "content": "Sen yardımcı bir asistansın." },
    { "role": "user", "content": "Merhaba, nasılsın?" },
    { "role": "assistant", "content": "Size nasıl yardımcı olabilirim?" },
    { "role": "user", "content": "Hava durumu nasıl?" },
    {
      "role": "assistant",
      "content": "Üzgünüm, gerçek zamanlı hava durumu bilgilerine erişimim yok. Bulunduğunuz konumun hava durumunu öğrenmek için hava durumu web sitelerini veya uygulamalarını kontrol edebilirsiniz."
    }
  ],
  "promptsafe_metadata": {
    "filtered_input": false,
    "filtered_output": false,
    "processing_time_ms": 1234.56,
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Yanıt Alanları

- `messages`: Güncellenmiş konuşma geçmişi. İstek mesajlarına ek olarak, LLM'den gelen yanıtı içerir.
- `promptsafe_metadata`: PromptSafe tarafından eklenen metadata.
  - `filtered_input`: Girdi metninde hassas veri tespit edilip filtrelendiğini belirtir.
  - `filtered_output`: Çıktı metninde hassas veri tespit edilip filtrelendiğini belirtir.
  - `processing_time_ms`: İşlem süresi (milisaniye).
  - `request_id`: İstek için benzersiz tanımlayıcı.

## Desteklenen Sağlayıcılar

### OpenAI

- **Provider**: `openai`
- **Varsayılan Model**: `gpt-3.5-turbo`
- **Desteklenen Modeller**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`
- **Özel Parametreler**:
  - `top_p`: Olasılık eşiği (0.0-1.0)
  - `frequency_penalty`: Kelime tekrarını azaltma (0.0-2.0)
  - `presence_penalty`: Konu tekrarını azaltma (0.0-2.0)

### Anthropic

- **Provider**: `anthropic`
- **Varsayılan Model**: `claude-3-haiku-20240307`
- **Desteklenen Modeller**: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- **Özel Parametreler**:
  - `top_k`: Dikkate alınacak maksimum token sayısı
  - `top_p`: Olasılık eşiği (0.0-1.0)

### Google

- **Provider**: `google`
- **Varsayılan Model**: `gemini-pro`
- **Desteklenen Modeller**: `gemini-pro`, `gemini-ultra`
- **Özel Parametreler**:
  - `top_k`: Dikkate alınacak maksimum token sayısı
  - `top_p`: Olasılık eşiği (0.0-1.0)

## Örnekler

### Basit MCP İsteği

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/proxy/mcp",
    json={
        "messages": [
            {"role": "user", "content": "Merhaba, dünya!"}
        ],
        "provider": "openai"
    }
)

print(response.json())
```

### Konuşma Geçmişi ile MCP İsteği

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/proxy/mcp",
    json={
        "messages": [
            {"role": "system", "content": "Sen yardımcı bir asistansın."},
            {"role": "user", "content": "Merhaba, nasılsın?"},
            {"role": "assistant", "content": "İyiyim, teşekkür ederim! Size nasıl yardımcı olabilirim?"},
            {"role": "user", "content": "Python'da dosya okuma nasıl yapılır?"}
        ],
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.5
    }
)

print(response.json())
```

### Farklı Sağlayıcı ile MCP İsteği

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/proxy/mcp",
    json={
        "messages": [
            {"role": "user", "content": "Yapay zeka nedir?"}
        ],
        "provider": "anthropic",
        "model": "claude-3-sonnet-20240229"
    }
)

print(response.json())
```

### Özel Parametreler ile MCP İsteği

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/proxy/mcp",
    json={
        "messages": [
            {"role": "user", "content": "Yaratıcı bir hikaye yaz."}
        ],
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.9,
        "max_tokens": 2000,
        "additional_params": {
            "top_p": 0.95,
            "frequency_penalty": 0.8,
            "presence_penalty": 0.5
        }
    }
)

print(response.json())
```
