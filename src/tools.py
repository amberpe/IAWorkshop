import os
import boto3
import uuid

def capture_lead(input):
    table_name = os.getenv("DYNAMODB_TABLE")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    
    input['id'] = str(uuid.uuid4())

    try:
        table.put_item(Item=input)
        return "✅ Item guardado con éxito."
    except Exception as e:
        return "❌ Error al guardar en DynamoDB: {e}"