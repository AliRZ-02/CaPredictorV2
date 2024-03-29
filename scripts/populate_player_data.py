import os
import aiohttp
import asyncio
import logging
import random
import requests
import scipy
import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from pymongo import MongoClient, ReplaceOne

# Dfine Global Variables & Constants
logger = logging.getLogger(__name__)

MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_APP = os.getenv("MONGO_APP")
PLAYER_LIST_URL = os.getenv("PLAYER_LIST_URL")


# Define Sync Helper Functions
def convert_time_to_float(time_str: str) -> float:
    data = time_str.split(":")
    mins, secs = data[0], data[1]

    return float(mins) + (float(secs) / 60)


def calculate_per60(value: float, toi: float, gp: int) -> float:
    return (value / (gp * toi)) * 60


def get_client():
    CONNECTION_STRING = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_URI}/?retryWrites=true&w=majority&appName={MONGO_APP}"
    return MongoClient(CONNECTION_STRING)


def get_players_ids():
    players = requests.get(PLAYER_LIST_URL).json()
    return [val["playerId"] for val in players if val.get("playerId")]


# Define helper global variables
mongo_client = get_client()
players = get_players_ids()


# Define global variables for data collection
player_original_stats = []
gamesPlayedArr = []
goalsArr = []
assistsArr = []
pmArr = []
pimArr = []
shotsArr = []
shotPctArr = []
ppArr = []
shArr = []
esArr = []
foArr = []
toiArr = []


# Define Async Helper Functions
async def request_player_stats(playerId: int, session: aiohttp.ClientSession) -> None:
    global player_original_stats
    global gamesPlayedArr
    global goalsArr
    global assistsArr
    global pmArr
    global pimArr
    global shotsArr
    global shotPctArr
    global ppArr
    global shArr
    global esArr
    global foArr
    global toiArr

    try:

        link = f'https://api-web.nhle.com/v1/player/{playerId}/landing'
        await asyncio.sleep(random.random())
        async with session.get(link) as resp:
            data = await resp.json()

            birthDate = data.get("birthDate")
            birthDate = datetime.strptime(birthDate, "%Y-%m-%d") if birthDate else None

            regSeasonStats = [season for season in data.get("seasonTotals", []) if season.get("gameTypeId") == 2 and season.get("leagueAbbrev") == "NHL"]
            latestSeason = regSeasonStats[-1] if regSeasonStats else {}

            if not latestSeason:
                return
            
            gamesPlayed = latestSeason.get("gamesPlayed")
            avgToi = latestSeason.get("avgToi")
            if not gamesPlayed or not avgToi:
                return
            
            toi = convert_time_to_float(avgToi)
            if toi is not None:
                toiArr.append(toi)
            else: 
                return
            
            gamesPlayedArr.append(gamesPlayed)

            goals = latestSeason.get("goals")
            if goals is not None:
                goals = calculate_per60(goals, toi, gamesPlayed)
                goalsArr.append(goals)
            
            assists = latestSeason.get("assists")
            if assists is not None:
                assists = calculate_per60(assists, toi, gamesPlayed)
                assistsArr.append(assists)
            
            pm = latestSeason.get("plusMinus")
            if pm is not None:
                pm = calculate_per60(pm, toi, gamesPlayed)
                pmArr.append(pm)
            
            pim = latestSeason.get("pim")
            if pim is not None:
                pim = calculate_per60(pim, toi, gamesPlayed)
                pimArr.append(pim)
            
            shots = latestSeason.get("shots")
            if shots is not None:
                shots = calculate_per60(shots, toi, gamesPlayed)
                shotsArr.append(shots)
            
            shotPct = latestSeason.get("shootingPctg")
            if shotPct is not None:
                shotPctArr.append(shotPct)
            
            pp = latestSeason.get("powerPlayPoints", 0)
            if pp is not None:
                pp = calculate_per60(pp, toi, gamesPlayed)
                ppArr.append(pp)
            
            sh = latestSeason.get("shorthandedPoints", 0)
            if sh is not None:
                sh = calculate_per60(sh, toi, gamesPlayed)
                shArr.append(sh)
            
            es = latestSeason.get("points", 0) - pp - sh
            if es is not None:
                es = calculate_per60(es, toi, gamesPlayed)
                esArr.append(es)
            
            fo = latestSeason.get("faceoffWinningPctg")
            if fo is not None:
                foArr.append(fo)

            player_original_stats.append(
                {
                    "players": {
                        "playerId": playerId,
                        "playerDetails": {
                            "playerName": f'{data.get("firstName")} {data.get("lastName")}',
                            "playerNumber": data.get("sweaterNumber"),
                            "position": data.get("position"),
                            "age": relativedelta(datetime.now(), birthDate).years if birthDate else None,
                            "height": data.get("heightInCentimeters"),
                            "weight": data.get("weightInKilograms")
                        },
                        "birthInformation": {
                            "country": data.get("birthCountry"),
                            "city": data.get("birthCity"),
                        },
                        "historicalData": {
                            "year": data.get("draftDetails", {}).get("year"),
                            "round": data.get("draftDetails", {}).get("round"),
                            "pickInRound": data.get("draftDetails", {}).get("pickInRound")
                        },
                        "photoDetails": {
                            "teamLogo": data.get("teamLogo"),
                            "headShotUrl": data.get("headshot"),
                            "imageUrl": data.get("heroImage")
                        }
                    },
                    "stats": {
                        "playerId": playerId,
                        "gamesPlayed": gamesPlayed,
                        "goalsPer60": goals,
                        "assistsPer60": assists,
                        "PlusMinusPer60": pm,
                        "PenaltyMinutesPer60": pim,
                        "ShotsPer60": shots,
                        "ShootingPercentage": shotPct,
                        "PowerPlayPer60": pp,
                        "ShortHandedPer60": sh,
                        "EvenStrengthPer60": es,
                        "FaceOffPercentage": fo,
                        "TimeOnIce": toi,
                    }
                }
                
            )
    except Exception as e:
        logger.warning(f"Couldn't request data for player {playerId}: {str(e)}")
        return


async def request_all_players():
    global players
    async with aiohttp.ClientSession() as session:
        tasks = []
        for player in players:
            tasks.append(asyncio.ensure_future(request_player_stats(int(player), session)))

        await asyncio.gather(*tasks)


# Upsert Helper Function
def upsert_player_data():
    global mongo_client

    players_to_upsert = []
    stats_to_upsert = []
    for player in player_original_stats:
        try:
            if player.get("stats"):
                stats_percentiles = {
                    "playerId": player["stats"]["playerId"],
                    "gamesPlayed": scipy.stats.percentileofscore(gamesPlayedArr, player["stats"]["gamesPlayed"]) if player["stats"].get("gamesPlayed") is not None else None,
                    "goalsPer60": scipy.stats.percentileofscore(goalsArr, player["stats"]["goalsPer60"]) if player["stats"].get("goalsPer60") is not None else None,
                    "assistsPer60": scipy.stats.percentileofscore(assistsArr, player["stats"]["assistsPer60"]) if player["stats"].get("assistsPer60") is not None else None,
                    "PlusMinusPer60": scipy.stats.percentileofscore(pmArr, player["stats"]["PlusMinusPer60"]) if player["stats"].get("PlusMinusPer60") is not None else None,
                    "PenaltyMinutesPer60": scipy.stats.percentileofscore(pimArr, player["stats"]["PenaltyMinutesPer60"]) if player["stats"].get("PenaltyMinutesPer60") is not None else None,
                    "ShotsPer60": scipy.stats.percentileofscore(shotsArr, player["stats"]["ShotsPer60"]) if player["stats"].get("ShotsPer60") is not None else None,
                    "ShootingPercentage": scipy.stats.percentileofscore(shotPctArr, player["stats"]["ShootingPercentage"]) if player["stats"].get("ShootingPercentage") is not None else None,
                    "PowerPlayPer60": scipy.stats.percentileofscore(ppArr, player["stats"]["PowerPlayPer60"]) if player["stats"].get("PowerPlayPer60") is not None else None,
                    "ShortHandedPer60": scipy.stats.percentileofscore(shArr, player["stats"]["ShortHandedPer60"]) if player["stats"].get("ShortHandedPer60") is not None else None,
                    "EvenStrengthPer60": scipy.stats.percentileofscore(esArr, player["stats"]["EvenStrengthPer60"]) if player["stats"].get("EvenStrengthPer60") is not None else None,
                    "FaceOffPercentage": scipy.stats.percentileofscore(foArr, player["stats"]["FaceOffPercentage"]) if player["stats"].get("FaceOffPercentage") is not None else None,
                    "TimeOnIce": scipy.stats.percentileofscore(toiArr, player["stats"]["TimeOnIce"]) if player["stats"].get("TimeOnIce") is not None else None,
                }

                stats_to_upsert.append(
                ReplaceOne(
                    {"playerId": player["stats"]["playerId"]},
                    stats_percentiles,
                    upsert=True
                )
            )
            
            if player.get("players"):
                players_to_upsert.append(
                    ReplaceOne(
                        {"playerId": player["players"]["playerId"]},
                        player["players"],
                        upsert=True
                    )
                )
        except Exception as e:
            logger.warning(f"Couldn't upsert player into mongo: {e}")
            continue
    
    # db + collections
    db = mongo_client["test"]
    player_collection = db.players
    stats_collection = db.stats

    # Bulk write
    player_collection.bulk_write(players_to_upsert)
    stats_collection.bulk_write(stats_to_upsert)

    return len(players_to_upsert), len(stats_to_upsert)


# Main Function
def update_player_stats():
    # Get Data
    t1 = time.time()
    asyncio.run(request_all_players())
    t2 = time.time()

    request_stats = {
        "player_original_stats": len(player_original_stats),
        "gamesPlayedArr": len(gamesPlayedArr),
        "goalsArr": len(goalsArr),
        "assistsArr": len(assistsArr),
        "pmArr": len(pmArr),
        "pimArr": len(pimArr),
        "shotsArr": len(shotsArr),
        "shotPctArr": len(shotPctArr),
        "ppArr": len(ppArr),
        "shArr": len(shArr),
        "esArr": len(esArr),
        "foArr": len(foArr),
        "toiArr": len(toiArr),
        "players": len(players)
    }

    logger.warning(f'Requested Stats in {t2 - t1} seconds: {request_stats}')

    # Upload Data
    t3 = time.time()
    players_upserted, stats_upserted = upsert_player_data()
    t4 = time.time()

    logger.warning(f'Upserted into Mongo in {t4 - t3} seconds: {players_upserted} players and {stats_upserted} stats')


if __name__ == "__main__":
    update_player_stats()