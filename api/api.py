from flask import Flask, request
from difflib import get_close_matches
from getter import request_players, request_players_by_id, get_player_stats, get_player_position
from constants import API_CODES
from predict import Predictor
from model import Player
from enum import Enum


api = Flask(__name__)


@api.route("/predict", methods=['POST'])
async def predict():
    request_data = request.get_json()
    player_name = request_data.get("player_name", None)
    contract_length = request_data.get("contract_length", 5)

    if not player_name:
        return {"error": "No player_name was specified"}, API_CODES.BAD_REQUEST.value
    elif not isinstance(player_name, str):
        return {"error": "player_name must be a string"}, API_CODES.BAD_REQUEST.value
    
    if not contract_length:
        return {"error": "No contract_length was specified"}, API_CODES.BAD_REQUEST.value
    elif not isinstance(contract_length, int):
        return {"error": "contract_length must be an integer"}, API_CODES.BAD_REQUEST.value
    
    player_dict = await players_dict()
    player_list = [key for key in player_dict]
    closest_player = get_close_matches(player_name, player_list, 1)

    if not closest_player:
        return {"error": f"No player was found with the name: {player_name}"}, API_CODES.NOT_FOUND.value
    
    player_id = player_dict[closest_player[0]]
    player_stats = await get_player_stats(player_id)
    player_position = await get_player_position(player_id)

    if player_stats is None:
        return {"error": f"Could not generate enough stats for player: {player_name}"}, API_CODES.NOT_FOUND.value
    
    predictor = Predictor(Player(closest_player[0], player_stats, player_position), contract_length, is_linreg=False)

    ret = predictor.get_prediction(), API_CODES.SUCCESS.value

    if ret and isinstance(ret[0].get("player", {}).get("position", None), Enum):
        ret[0]["player"]["position"] = ret[0]["player"]["position"].value

    return ret if ret[0].get("error", None) is None else (ret[0], API_CODES.CALCULATION_ERROR.value)


@api.route("/players")
async def players():
    data = await players_dict()

    return [key for key in data], API_CODES.SUCCESS.value


@api.route("/clear_cache")
async def clear_cache():
    try:
        get_player_stats.cache_clear()
        get_player_position.cache_clear()
        request_players.cache_clear()
        request_players_by_id.cache_clear()
    except:
        return {"error": "Could not clear async LRU cache"}, API_CODES.CACHE_ERROR.value
    else:
        return {"message": "Cache successfully cleared"}, API_CODES.SUCCESS.value


async def players_dict():
    data = await request_players()

    return {
        item.get("name", None): item.get("playerId", None) 
        for item in data if item.get("name", None) is not None
    }
    

if __name__ == "__main__":
    from waitress import serve
    serve(api, host="0.0.0.0", port=5000)