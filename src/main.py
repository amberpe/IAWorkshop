from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler    import APIGatewayRestResolver
from aws_lambda_powertools.logging          import correlation_paths
from aws_lambda_powertools.metrics          import MetricUnit
from aws_lambda_powertools                  import Metrics
from aws_lambda_powertools                  import Logger
from aws_lambda_powertools                  import Tracer
from concurrent.futures                     import ThreadPoolExecutor
import boto3
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
            "description": "Captures lead information including name, phone number and interest.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the user with and interest."
                    },
                    "phone": {
                        "type": "string",
                        "description": "User's phone number. This will be usually from Peru."
                    },
                    "interest": {
                        "type": "string",
                        "description": "User's necesity."
                    }
                },
                "required": ["name", "phone", "interest"]
            }
        }
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
            'system': """Eres Ambercito un agente especialista en ventas.
Tu tarea es asesorar a los clientes sobre dudas que tengan al buscar su producto tecnológico ideal.
El cliente va a decirte cuál es su necesidad / problema.
Debes responder en un tono amable, con respuestas breves, claras y útiles."""
            })
        )
    
    mensaje = json.loads(response["body"].read().decode("utf-8"))
    
    metrics.add_metric(name="IncomingMessage", unit=MetricUnit.Count, value=1)
    return {
        "statusCode": 200,
        "body": mensaje
    }

import tools

@app.post("/tool")
@tracer.capture_method
def tool():
    body = json.loads(app.current_event.body)
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
