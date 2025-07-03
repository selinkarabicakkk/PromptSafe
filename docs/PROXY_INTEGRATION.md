# PromptSafe Proxy Entegrasyonu

Bu dokümantasyon, PromptSafe'in proxy özelliğini nasıl entegre edeceğinizi ve kullanacağınızı açıklar.

## İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Entegrasyon Seçenekleri](#entegrasyon-seçenekleri)
   - [Tarayıcı Eklentisi](#tarayıcı-eklentisi)
   - [Sistem Proxy](#sistem-proxy)
   - [API Entegrasyonu](#api-entegrasyonu)
3. [Model-Context-Protocol (MCP)](#model-context-protocol-mcp)
4. [Örnek Senaryolar](#örnek-senaryolar)
5. [Sorun Giderme](#sorun-giderme)

## Genel Bakış

PromptSafe proxy'si, kullanıcıların LLM (Büyük Dil Modelleri) hizmetlerine erişimini şeffaf bir şekilde yöneterek hassas verilerin korunmasını sağlar. Proxy, kullanıcılar ile LLM sağlayıcıları arasında bir aracı olarak çalışır:

1. Kullanıcı isteği PromptSafe proxy'sine yönlendirilir
2. Proxy, istek metnindeki hassas verileri tespit eder ve maskeler
3. Filtrelenmiş istek, LLM sağlayıcısına gönderilir
4. LLM'den gelen yanıt tekrar proxy tarafından filtrelenir
5. Filtrelenmiş yanıt kullanıcıya iletilir

Bu akış, kullanıcıların normal LLM deneyimini bozmadan hassas verilerin korunmasını sağlar.

## Entegrasyon Seçenekleri

### Tarayıcı Eklentisi

Tarayıcı eklentisi, ChatGPT, Claude veya Gemini gibi web tabanlı LLM arayüzlerini kullanırken hassas verileri otomatik olarak filtreler.

#### Kurulum

1. Tarayıcı eklentisini derleyin:

```bash
cd browser-extension
npm install
npm run build
```

2. Oluşturulan `dist` klasöründeki eklentiyi tarayıcınıza yükleyin:

   - Chrome: `chrome://extensions/` adresine gidin, "Geliştirici modu"nu etkinleştirin ve "Paketlenmemiş öğe yükle" seçeneğiyle `dist` klasörünü seçin.
   - Firefox: `about:debugging#/runtime/this-firefox` adresine gidin, "Geçici Eklenti Yükle" seçeneğiyle `dist/manifest.json` dosyasını seçin.
   - Edge: `edge://extensions/` adresine gidin, "Geliştirici modu"nu etkinleştirin ve "Paketlenmemiş öğe yükle" seçeneğiyle `dist` klasörünü seçin.

3. Eklenti ayarlarından PromptSafe sunucu adresini yapılandırın (varsayılan: `http://localhost:8000`).

#### Kullanım

Eklenti yüklendikten sonra, tarayıcınızda ChatGPT, Claude veya Gemini web arayüzlerini normal şekilde kullanabilirsiniz. Eklenti, tüm istekleri ve yanıtları otomatik olarak PromptSafe üzerinden yönlendirir.

### Sistem Proxy

Sistem proxy'si, tüm LLM trafiğini PromptSafe üzerinden yönlendirerek işletim sistemi seviyesinde hassas verileri filtreler.

#### Etkinleştirme

```bash
# Sistem proxy'sini etkinleştirmek için:
curl -X POST http://localhost:8000/api/v1/system-proxy/enable
```

Bu komut, işletim sisteminizin proxy ayarlarını PromptSafe'e yönlendirecek şekilde yapılandırır.

#### Devre Dışı Bırakma

```bash
# Sistem proxy'sini devre dışı bırakmak için:
curl -X POST http://localhost:8000/api/v1/system-proxy/disable
```

Bu komut, işletim sisteminizin proxy ayarlarını normal haline döndürür.

### API Entegrasyonu

Kendi uygulamanızı PromptSafe API'sine entegre ederek hassas verileri filtreleyebilirsiniz.

#### MCP Formatında İstek

```python
import requests

# MCP formatında istek
response = requests.post(
    "http://localhost:8000/api/v1/proxy/mcp",
    json={
        "messages": [
            {"role": "system", "content": "Sen yardımcı bir asistansın."},
            {"role": "user", "content": "Merhaba, benim adım John Doe ve email adresim john.doe@example.com"}
        ],
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "temperature": 0.7,
        "max_tokens": 1024
    }
)

print(response.json())
```

#### Standart API İsteği

```python
import requests

# OpenAI API formatında istek
response = requests.post(
    "http://localhost:8000/api/v1/proxy/openai/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        # API anahtarı PromptSafe tarafından otomatik olarak eklenir
    },
    json={
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Merhaba, benim adım John Doe ve email adresim john.doe@example.com"}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
)

print(response.json())
```

## Model-Context-Protocol (MCP)

Model-Context-Protocol (MCP), farklı LLM sağlayıcıları için standart bir iletişim protokolüdür. PromptSafe, MCP formatındaki istekleri destekler ve farklı LLM sağlayıcılarına uygun şekilde dönüştürür.

### MCP İstek Formatı

```json
{
  "messages": [
    { "role": "system", "content": "Sen yardımcı bir asistansın." },
    { "role": "user", "content": "Merhaba, nasılsın?" }
  ],
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

### MCP Yanıt Formatı

```json
{
  "messages": [
    { "role": "system", "content": "Sen yardımcı bir asistansın." },
    { "role": "user", "content": "Merhaba, nasılsın?" },
    {
      "role": "assistant",
      "content": "Merhaba! Ben bir yapay zeka asistanıyım, bu yüzden duygularım yok ama size yardımcı olmak için buradayım. Size nasıl yardımcı olabilirim?"
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

## Örnek Senaryolar

### Senaryo 1: Web Uygulaması Entegrasyonu

```javascript
// React uygulamasında PromptSafe entegrasyonu
async function sendMessage(message) {
  const response = await fetch("http://localhost:8000/api/v1/proxy/mcp", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messages: [{ role: "user", content: message }],
      model: "gpt-3.5-turbo",
      provider: "openai",
    }),
  });

  const data = await response.json();
  return data.messages[data.messages.length - 1].content;
}
```

### Senaryo 2: CLI Uygulaması

```python
import argparse
import requests
import json

def main():
    parser = argparse.ArgumentParser(description='PromptSafe CLI')
    parser.add_argument('prompt', help='Prompt to send to LLM')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='Model to use')
    parser.add_argument('--provider', default='openai', help='Provider to use (openai, anthropic, google)')

    args = parser.parse_args()

    response = requests.post(
        "http://localhost:8000/api/v1/proxy/mcp",
        json={
            "messages": [
                {"role": "user", "content": args.prompt}
            ],
            "model": args.model,
            "provider": args.provider
        }
    )

    result = response.json()
    print(result["messages"][-1]["content"])

if __name__ == "__main__":
    main()
```

### Senaryo 3: WebSocket Bağlantısı

```javascript
// WebSocket bağlantısı ile gerçek zamanlı filtreleme
const socket = new WebSocket("ws://localhost:8000/ws/client-123");

socket.onopen = () => {
  console.log("WebSocket bağlantısı açıldı");

  // MCP formatında istek gönder
  socket.send(
    JSON.stringify({
      type: "prompt",
      data: {
        messages: [
          {
            role: "user",
            content:
              "Merhaba, benim adım John Doe ve email adresim john.doe@example.com",
          },
        ],
        model: "gpt-3.5-turbo",
        provider: "openai",
      },
    })
  );
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "response") {
    console.log(
      "Yanıt:",
      data.data.messages[data.data.messages.length - 1].content
    );
  } else if (data.type === "error") {
    console.error("Hata:", data.error);
  }
};

socket.onclose = () => {
  console.log("WebSocket bağlantısı kapatıldı");
};
```

## Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

1. **Bağlantı Hatası**

   Sorun: PromptSafe sunucusuna bağlanılamıyor.

   Çözüm: PromptSafe sunucusunun çalıştığından ve doğru port üzerinden erişilebilir olduğundan emin olun.

   ```bash
   # PromptSafe durumunu kontrol et
   curl http://localhost:8000/api/v1/health
   ```

2. **API Anahtarı Hatası**

   Sorun: LLM sağlayıcısına istek gönderilirken API anahtarı hatası alınıyor.

   Çözüm: `.env` dosyasında ilgili API anahtarının doğru şekilde ayarlandığından emin olun.

3. **Proxy Ayarları Etkinleştirilemiyor**

   Sorun: Sistem proxy ayarları etkinleştirilemiyor.

   Çözüm: PromptSafe'i yönetici (admin) haklarıyla çalıştırın veya manuel olarak proxy ayarlarını yapılandırın.

4. **Tarayıcı Eklentisi Çalışmıyor**

   Sorun: Tarayıcı eklentisi istekleri yakalamıyor.

   Çözüm: Eklenti ayarlarından PromptSafe sunucu adresinin doğru olduğundan emin olun ve tarayıcıyı yeniden başlatın.

### Loglama

PromptSafe, detaylı loglar tutar. Sorun giderme için logları kontrol edin:

```bash
# Log seviyesini DEBUG olarak ayarlayın
export LOG_LEVEL=DEBUG

# Uygulamayı başlatın
uvicorn app.main:app --reload
```
