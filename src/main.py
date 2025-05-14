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
    
@app.post("/converse")
@tracer.capture_method
def converse():
    # Obtener el array de mensajes del request body
    messages = json.loads(app.current_event.body)["chat_history"]
    
    print(messages)
    
    # Definir las herramientas
    
    tools = [
        {
            "name": "capture_lead",
            "description": "Captures lead information including name, phone number, email, and interest.",
            "parameters": {
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
        },
        {
            "name": "search_recommendations",
            "description": "Busca recomendaciones basadas en la necesidad del usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "interest": {
                        "type": "string",
                        "description": "La necesidad del usuario."
                    }
                },
                "required": ["interest"]
            }
        }
    ]
    
    # Cliente de bedrock
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=AWS_REGION)
    
    # Llamar a bedrock
    response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body={
            "anthropic_version": "bedrock-2023-05-31",
            'max_tokens': 524,
            'messages': messages,
            'temperature': 0,
            'system': """Eres un agente llamado Workshopcito y trabajas como ayudante de ventas en la empresa IA Ventas.
La empresa IA Ventas es una tienda retail que vende productos físicos como flores, ferretería, libros, entre otros.
Tu tarea principal es proporcionar atención al cliente 24/7, asesorar sobre productos, responder preguntas, hacer seguimientos
de leads y mejorar las ventas mediante un servicio eficiente, siempre dentro del marco de la seguridad y la privacidad de la empresa.

Tu tono debe ser amigable, profesional y útil. Debes adaptarte al tono de la empresa y comunicarte de manera clara y concisa. Siempre mantén un enfoque en el cliente y su experiencia, evitando respuestas demasiado formales o impersonales. Usa emojis.
""",
            'tools': tools
        }
        )
    
    mensaje = response["body"].read().decode("utf-8")
    print(mensaje)
    
    # metrics.add_metric(name="IncomingMessage", unit=MetricUnit.Count, value=1)
    return {
        "statusCode": 200,
        "body": "pong"
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
