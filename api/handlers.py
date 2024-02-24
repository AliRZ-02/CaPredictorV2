from api import predict, players

def predict_handler(event, context):
    return {"statusCode": 200, "body": predict()}

def players_handler(event, context):
    return {"statusCode": 200, "body": players()}
