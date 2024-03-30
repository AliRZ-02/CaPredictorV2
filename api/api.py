from difflib import get_close_matches
from getter import request_players, request_players_by_id, get_player_stats, get_player_position
from constants import API_CODES
from predict import Predictor
from model import Player
from enum import Enum

def predict(request_data):
    """
    {
        "player_name": <str>,
        "contract_length": <int>
    }
    """
    try:
        player_name = request_data.get("player_name", None)
        contract_length = int(request_data.get("contract_length", 5))
    except:
        return {"error": "Invalid Request Arguments"}

    if not player_name:
        return {"error": "No player_name was specified"}, API_CODES.BAD_REQUEST.value
    elif not isinstance(player_name, str):
        return {"error": "player_name must be a string"}, API_CODES.BAD_REQUEST.value
    
    if not contract_length:
        return {"error": "No contract_length was specified"}, API_CODES.BAD_REQUEST.value
    elif not isinstance(contract_length, int):
        return {"error": "contract_length must be an integer"}, API_CODES.BAD_REQUEST.value
    
    player_dict = players_dict()
    player_list = [key for key in player_dict]
    closest_player = get_close_matches(player_name, player_list, 1)

    if not closest_player:
        return {"error": f"No player was found with the name: {player_name}"}, API_CODES.NOT_FOUND.value
    
    player_id = player_dict[closest_player[0]]
    player_stats = get_player_stats(player_id)
    player_position = get_player_position(player_id)

    if player_stats is None:
        return {"error": f"Could not generate enough stats for player: {player_name}"}, API_CODES.NOT_FOUND.value
    
    predictor = Predictor(Player(closest_player[0], player_stats, player_position), contract_length, is_linreg=True)

    ret = predictor.get_prediction(), API_CODES.SUCCESS.value

    if ret and isinstance(ret[0].get("player", {}).get("position", None), Enum):
        ret[0]["player"]["position"] = ret[0]["player"]["position"].value

    return ret if ret[0].get("error", None) is None else (ret[0], API_CODES.CALCULATION_ERROR.value)


def players():
    data = players_dict()

    return [key for key in data], API_CODES.SUCCESS.value


def players_dict():
    data = request_players()

    toReturn = {}
    duplicates = {}
    for item in data:
        if item.get("name", None) is not None:
            if item["name"] not in toReturn:
                toReturn[item["name"]] = item.get("playerId")
            else:
                duplicates[item["name"]] = duplicates.get(item["name"], 0) + 1
                toReturn[f'{item["name"]} ({duplicates[item["name"]]})'] = item.get("playerId")

    return toReturn
