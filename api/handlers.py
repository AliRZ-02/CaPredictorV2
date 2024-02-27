from api import predict, players

def predict_handler(event, context):
    try:
        return {"statusCode": 200, "body": predict(event['queryStringParameters'])}
    except Exception as e:
        return {"error": str(e)}

def players_handler(event, context):
    try:
        return {"statusCode": 200, "body": players()}
    except Exception as e:
        return {"error": str(e)}
