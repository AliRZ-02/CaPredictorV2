from api import predict, players_dict

def predict_handler(event, context):
    try:
        return {"statusCode": 200, "body": predict(event['queryStringParameters'])}
    except Exception as e:
        return {"error": str(e)}

def players_handler(event, context):
    try:
        return {"statusCode": 200, "body": [{"name": key, "playerId": value} for key, value in players_dict().items()]}
    except Exception as e:
        return {"error": str(e)}
