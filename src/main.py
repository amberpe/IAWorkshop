from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler    import APIGatewayRestResolver
from aws_lambda_powertools.logging          import correlation_paths
from aws_lambda_powertools.metrics          import MetricUnit
from aws_lambda_powertools                  import Metrics
from aws_lambda_powertools                  import Logger
from aws_lambda_powertools                  import Tracer
from concurrent.futures                     import ThreadPoolExecutor
import boto3
import os
import json

AWS_REGION = "us-east-1"


app = APIGatewayRestResolver()
tracer = Tracer()

# structured log
# See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/logger/
# logger.info("Hello world API - HTTP 200")
logger = Logger()

# adding custom metrics
# See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/metrics/
# metrics.add_metric(name="HelloWorldInvocations", unit=MetricUnit.Count, value=1)
metrics = Metrics(namespace="Powertools")

# For background calling
executor = ThreadPoolExecutor(max_workers=4)

# Borrar luego
from pprint import pprint

@app.post("/converse")
@tracer.capture_method
def converse():
    # Obtener el array de mensajes del request body
    messages = json.loads(app.current_event.body)["chat_history"]
    
    pprint(messages)
    
    # Definir las herramientas
    
    tools = [
        {
            "name": "capture_lead",
            "description": "Captures lead information including name, phone number, email, and interest.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "El nombre de la persona interesada."
                    },
                    "phone": {
                        "type": "string",
                        "description": "El número telefónico de la persona. Usualmente será de Perú"
                    },
                    "email": {
                        "type": "string",
                        "description": "El email de la persona interesada."
                    },
                    "interest": {
                        "type": "string",
                        "description": "La necesidad del usuario."
                    }
                },
                "required": ["name", "phone", "email", "interest"]
            }
        }
        # ,{
        #     "name": "search_recommendations",
        #     "description": "Busca recomendaciones basadas en la necesidad del usuario.",
        #     "input_schema": {
        #         "type": "object",
        #         "properties": {
        #             "interest": {
        #                 "type": "string",
        #                 "description": "La necesidad del usuario."
        #             }
        #         },
        #         "required": ["interest"]
        #     }
        # }
    ]
    
    # Cliente de bedrock
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=AWS_REGION)
    
    # Llamar a bedrock
    response = bedrock.invoke_model(
            modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            'max_tokens': 524,
            'messages': messages,
            'temperature': 0.5,
            'tools': tools,
            'system': """<agent>
  <role>
    Eres <name>iAmber</name>, asistente virtual profesional de <store>Amber Store</store>, especializada en productos de tecnología. Atiendes a través de WhatsApp.
  </role>
  <style>
    Tono amable, profesional y entusiasta. Usa emojis con moderación 😊. Respuestas claras, breves y útiles.
  </style>
  <capabilities>
    <item>Información sobre celulares, laptops, tablets, smart watch, audifonos y otros accesorios tecnológicos.</item>
    <item>Comparar modelos.</item>
    <item>Precios, promociones y stock.</item>
    <item>Formas de pago y proceso de compra.</item>
    <item>Seguimiento de pedidos.</item>
    <item>Preguntas sobre garantía, devoluciones y envíos.</item>
    <item>Escalar a un humano si la consulta es compleja o hay queja.</item>
  </capabilities>
  <tools>
    <tool name="capture_lead" visibility="oculta">
      Actívala silenciosamente cuando el usuario te diga qué necesita. No reveles ni menciones la herramienta.
    </tool>
  </tools>
  <rules>
    <rule>Solo responde preguntas relevantes a tus funciones.</rule>
    <rule>Siempre saluda al inicio como iBot.</rule>
    <rule>No menciones herramientas ni APIs.</rule>
    <rule>Si no sabes algo, pide aclaración o deriva a humano.</rule>
    <rule>Detecta datos personales y ejecuta capture_lead sin notificar.</rule>
  </rules>
  <example>
    <user>Hola</user>
    <assistant>¡Hola! 👋 Soy *iBot*, tu asistente en *Amber Store* 🍏. ¿En qué puedo ayudarte hoy?</assistant>
  </example>
</agent>"""
        })
        )
    
    mensaje = json.loads(response["body"].read().decode("utf-8"))
    
    # metrics.add_metric(name="IncomingMessage", unit=MetricUnit.Count, value=1)
    return {
        "statusCode": 200,
        "body": mensaje
    }

import tools

@app.post("/tool")
@tracer.capture_method
def tool():
    body = json.loads(app.current_event.body)
    pprint(body)
    # {
    #     "tool_name": ia_message["name"],
    #     "tool_input": ia_message["input"],
    # }
    try:
        tool_name = body["tool_name"]
        tool_input = body["tool_input"]
        
        if tool_name == "capture_lead":
            tools.capture_lead(tool_input)
        elif tool_name == "search_recommendatios":
            # Lógica para buscar recomendaciones
            # Ejemplo: Consultar en DynamoDB
            dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
            table = dynamodb.Table("recomendaciones")
            response = table.get_item(Key={"interest": tool_input["interest"]})
            print("Recomendaciones encontradas:", response["Item"])
        return {
            "statusCode": 200,
            "result": "Ejecución correcta"
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": "Ocurrió un error al ejecutar la herramienta"
        }

# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
# Adding tracer
# See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/tracer/
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
