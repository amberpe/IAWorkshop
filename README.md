# iAmber AI Agent API 🤖✨

Esta es una API REST para un agente de inteligencia artificial llamado **iAmber**, un asistente virtual profesional de **Amber Store**, especializada en productos tecnológicos. Atiende a través de WhatsApp, procesando interacciones con usuarios, capturando leads de forma automática y respondiendo con tono profesional, breve y amigable.

## 📌 Características

- Construido con **FastAPI**.
- Uso de **Amazon Bedrock (Claude 3.5 Sonnet)** como modelo de lenguaje.
- Herramienta personalizada `capture_lead` para captar datos clave del cliente.
- Tono natural y profesional con emojis moderados 😊.
- Enrutamiento limpio con soporte para trazabilidad (decorador `@tracer.capture_method`).

---

## 📦 Requisitos

- Python 3.11 o superior
- AWS CLI configurado (`aws configure`) o CloudShell
- Cuenta con acceso a **Bedrock Runtime**

---

## 🚀 Ejecución local

Puedes correr la API localmente usando SAM:

```bash
sam local start-api
```

Recuerda que requieres `Docker`.

---

## 🔁 Endpoint principal

### `POST /converse`

Este endpoint recibe un historial de conversación (`chat_history`) y devuelve una respuesta generada por el modelo de lenguaje.

#### 🧾 Cuerpo del request (`JSON`)
```json
  {
    "chat_history": [
      {
        "role": "user",
        "content": "Hola, estoy interesado en un celular."
      },
      {
        "role": "assistant",
        "content": "¡Hola! 👋 Soy iBot, tu asistente en Amber Store. ¿Qué tipo de celular buscas?"
      },
      {
        "role": "user",
        "content": "Uno gama media"
      }
    ]
  }
```

## 🛠️ Herramientas disponibles (invisibles para el usuario)

### `capture_lead`

Captura información del cliente sin que se notifique explícitamente en la conversación.

```json
{
  "name": "capture_lead",
  "description": "Captures lead information including name, phone number and interest.",
  "input_schema": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "phone": { "type": "string" },
      "interest": { "type": "string" }
    },
    "required": ["name", "phone", "interest"]
  }
}
```

---

## 🧠 System Prompt del Agente

El sistema guía el comportamiento del asistente, incluyendo:
- Rol y nombre del asistente (*iBot*)
- Estilo conversacional profesional y claro
- Capacidades específicas de atención tecnológica
- Reglas para escalar, no responder fuera de su dominio, y capturar leads

---

## 📈 Métricas

Se registra el número de mensajes entrantes con:
```python
metrics.add_metric(name="IncomingMessage", unit=MetricUnit.Count, value=1)
```

---

## 📍 Despliegue

Este proyecto se integra con **AWS Lambda** usando **AWS Lambda Powertools** y API Gateway para producción.

Al usar SAM podemos desplegarlo en CloudShell con **un solo click**.

Copiar, pegar y ejecutar el siguiente comando:

```sh
git clone https://github.com/amberpe/IAWorkshop && cd IAWorkshop && source ./deploy.sh
```

---

## 🧪 Pruebas

Próximamente: se recomienda usar `pytest` y `httpx` para pruebas asincrónicas.

---
