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
gamesPlayedArrDefense = []
goalsArrDefense = []
assistsArrDefense = []
pmArrDefense = []
pimArrDefense = []
shotsArrDefense = []
shotPctArrDefense = []
ppArrDefense = []
shArrDefense = []
esArrDefense = []
foArrDefense = []
toiArrDefense = []
gaaArr = []
svPctArr = []
winPctArr = []
goaliesGamesPlayedArr = []


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
    global gamesPlayedArrDefense
    global goalsArrDefense
    global assistsArrDefense
    global pmArrDefense
    global pimArrDefense
    global shotsArrDefense
    global shotPctArrDefense
    global ppArrDefense
    global shArrDefense
    global esArrDefense
    global foArrDefense
    global toiArrDefense
    global gaaArr
    global svPctArr
    global winPctArr
    global goaliesGamesPlayedArr

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
            if not gamesPlayed:
                return

            position = data.get("position")
            if not position:
                return
            
            if position == "G":
                gaa = latestSeason.get("goalsAgainstAvg")
                if gaa is not None:
                    gaaArr.append(gaa)
                
                svPct = latestSeason.get("savePctg")
                if svPct is not None:
                    svPctArr.append(svPct)
                
                wins = latestSeason.get("wins")
                if wins is not None:
                    winPctArr.append(wins / gamesPlayed)
                
                goaliesGamesPlayedArr.append(gamesPlayed)
                
                player_stats = {
                    "playerId": playerId,
                    "gamesPlayed": gamesPlayed,
                    "goalsAgainstAverage": gaa,
                    "savePercentage": svPct,
                    "winPercentage": wins / gamesPlayed if wins is not None else None
                }
            else:
                avgToi = latestSeason.get("avgToi")
                if not avgToi:
                    return
                
                toi = convert_time_to_float(avgToi)
                if toi is not None:
                    if position == "D":
                        toiArrDefense.append(toi)
                    else:
                        toiArr.append(toi)
                else: 
                    return
                
                if position == "D":
                    gamesPlayedArrDefense.append(gamesPlayed)
                else:
                    gamesPlayedArr.append(gamesPlayed)

                goals = latestSeason.get("goals")
                if goals is not None:
                    goals = calculate_per60(goals, toi, gamesPlayed)

                    if position == "D":
                        goalsArrDefense.append(goals)
                    else:
                        goalsArr.append(goals)
                
                assists = latestSeason.get("assists")
                if assists is not None:
                    assists = calculate_per60(assists, toi, gamesPlayed)

                    if position == "D":
                        assistsArrDefense.append(assists)
                    else:
                        assistsArr.append(assists)
                
                pm = latestSeason.get("plusMinus")
                if pm is not None:
                    pm = calculate_per60(pm, toi, gamesPlayed)

                    if position == "D":
                        pmArrDefense.append(pm)
                    else:
                        pmArr.append(pm)
                
                pim = latestSeason.get("pim")
                if pim is not None:
                    pim = calculate_per60(pim, toi, gamesPlayed)

                    if position == "D":
                        pimArrDefense.append(pim)
                    else:
                        pimArr.append(pim)
                
                shots = latestSeason.get("shots")
                if shots is not None:
                    shots = calculate_per60(shots, toi, gamesPlayed)

                    if position == "D":
                        shotsArrDefense.append(shots)
                    else:
                        shotsArr.append(shots)
                
                shotPct = latestSeason.get("shootingPctg")
                if shotPct is not None:

                    if position == "D":
                        shotPctArrDefense.append(shotPct)
                    else:
                        shotPctArr.append(shotPct)
                
                pp = latestSeason.get("powerPlayPoints", 0)
                if pp is not None:
                    pp = calculate_per60(pp, toi, gamesPlayed)

                    if position == "D":
                        ppArrDefense.append(pp)
                    else:
                        ppArr.append(pp)
                
                sh = latestSeason.get("shorthandedPoints", 0)
                if sh is not None:
                    sh = calculate_per60(sh, toi, gamesPlayed)

                    if position == "D":
                        shArrDefense.append(sh)
                    else:
                        shArr.append(sh)
                
                es = latestSeason.get("points", 0) - pp - sh
                if es is not None:
                    es = calculate_per60(es, toi, gamesPlayed)

                    if position == "D":
                        esArrDefense.append(es)
                    else:
                        esArr.append(es)
                
                fo = latestSeason.get("faceoffWinningPctg")
                if fo is not None:

                    if position == "D":
                        foArrDefense.append(fo)
                    else:
                        foArr.append(fo)
                
                player_stats = {
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

            player_original_stats.append(
                {
                    "players": {
                        "playerId": playerId,
                        "playerDetails": {
                            "playerName": f'{data.get("firstName", {}).get("default")} {data.get("lastName", {}).get("default")}',
                            "playerNumber": data.get("sweaterNumber"),
                            "position": data.get("position"),
                            "age": relativedelta(datetime.now(), birthDate).years if birthDate else None,
                            "height": data.get("heightInCentimeters"),
                            "weight": data.get("weightInKilograms")
                        },
                        "birthInformation": {
                            "country": data.get("birthCountry"),
                            "city": data.get("birthCity", {}).get("default"),
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
                    "stats": player_stats
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
                if player.get("players", {}).get("playerDetails", {}).get("position") in ["C", "L", "R"]:
                    stats_percentiles = {
                        "playerId": player["stats"]["playerId"],
                        "gamesPlayed": round(scipy.stats.percentileofscore(gamesPlayedArr, player["stats"]["gamesPlayed"])) if player["stats"].get("gamesPlayed") is not None else None,
                        "goalsPer60": round(scipy.stats.percentileofscore(goalsArr, player["stats"]["goalsPer60"])) if player["stats"].get("goalsPer60") is not None else None,
                        "assistsPer60": round(scipy.stats.percentileofscore(assistsArr, player["stats"]["assistsPer60"])) if player["stats"].get("assistsPer60") is not None else None,
                        "PlusMinusPer60": round(scipy.stats.percentileofscore(pmArr, player["stats"]["PlusMinusPer60"])) if player["stats"].get("PlusMinusPer60") is not None else None,
                        "PenaltyMinutesPer60": 100 - round(scipy.stats.percentileofscore(pimArr, player["stats"]["PenaltyMinutesPer60"])) if player["stats"].get("PenaltyMinutesPer60") is not None else None,
                        "ShotsPer60": round(scipy.stats.percentileofscore(shotsArr, player["stats"]["ShotsPer60"])) if player["stats"].get("ShotsPer60") is not None else None,
                        "ShootingPercentage": round(scipy.stats.percentileofscore(shotPctArr, player["stats"]["ShootingPercentage"])) if player["stats"].get("ShootingPercentage") is not None else None,
                        "PowerPlayPer60": round(scipy.stats.percentileofscore(ppArr, player["stats"]["PowerPlayPer60"])) if player["stats"].get("PowerPlayPer60") is not None else None,
                        "ShortHandedPer60": round(scipy.stats.percentileofscore(shArr, player["stats"]["ShortHandedPer60"])) if player["stats"].get("ShortHandedPer60") is not None else None,
                        "EvenStrengthPer60": round(scipy.stats.percentileofscore(esArr, player["stats"]["EvenStrengthPer60"])) if player["stats"].get("EvenStrengthPer60") is not None else None,
                        "FaceOffPercentage": round(scipy.stats.percentileofscore(foArr, player["stats"]["FaceOffPercentage"])) if player["stats"].get("FaceOffPercentage") is not None else None,
                        "TimeOnIce": round(scipy.stats.percentileofscore(toiArr, player["stats"]["TimeOnIce"])) if player["stats"].get("TimeOnIce") is not None else None,
                    }
                elif player.get("players", {}).get("playerDetails", {}).get("position") == "D":
                    stats_percentiles = {
                        "playerId": player["stats"]["playerId"],
                        "gamesPlayed": round(scipy.stats.percentileofscore(gamesPlayedArrDefense, player["stats"]["gamesPlayed"])) if player["stats"].get("gamesPlayed") is not None else None,
                        "goalsPer60": round(scipy.stats.percentileofscore(goalsArrDefense, player["stats"]["goalsPer60"])) if player["stats"].get("goalsPer60") is not None else None,
                        "assistsPer60": round(scipy.stats.percentileofscore(assistsArrDefense, player["stats"]["assistsPer60"])) if player["stats"].get("assistsPer60") is not None else None,
                        "PlusMinusPer60": round(scipy.stats.percentileofscore(pmArrDefense, player["stats"]["PlusMinusPer60"])) if player["stats"].get("PlusMinusPer60") is not None else None,
                        "PenaltyMinutesPer60": 100 - round(scipy.stats.percentileofscore(pimArrDefense, player["stats"]["PenaltyMinutesPer60"])) if player["stats"].get("PenaltyMinutesPer60") is not None else None,
                        "ShotsPer60": round(scipy.stats.percentileofscore(shotsArrDefense, player["stats"]["ShotsPer60"])) if player["stats"].get("ShotsPer60") is not None else None,
                        "ShootingPercentage": round(scipy.stats.percentileofscore(shotPctArrDefense, player["stats"]["ShootingPercentage"])) if player["stats"].get("ShootingPercentage") is not None else None,
                        "PowerPlayPer60": round(scipy.stats.percentileofscore(ppArrDefense, player["stats"]["PowerPlayPer60"])) if player["stats"].get("PowerPlayPer60") is not None else None,
                        "ShortHandedPer60": round(scipy.stats.percentileofscore(shArrDefense, player["stats"]["ShortHandedPer60"])) if player["stats"].get("ShortHandedPer60") is not None else None,
                        "EvenStrengthPer60": round(scipy.stats.percentileofscore(esArrDefense, player["stats"]["EvenStrengthPer60"])) if player["stats"].get("EvenStrengthPer60") is not None else None,
                        "FaceOffPercentage": round(scipy.stats.percentileofscore(foArrDefense, player["stats"]["FaceOffPercentage"])) if player["stats"].get("FaceOffPercentage") is not None else None,
                        "TimeOnIce": round(scipy.stats.percentileofscore(toiArrDefense, player["stats"]["TimeOnIce"])) if player["stats"].get("TimeOnIce") is not None else None,
                    }
                else:
                    stats_percentiles = {
                        "playerId": player["stats"]["playerId"],
                        "gamesPlayed": round(scipy.stats.percentileofscore(goaliesGamesPlayedArr, player["stats"]["gamesPlayed"])) if player["stats"].get("gamesPlayed") is not None else None,
                        "goalsAgainstAverage": 100 - round(scipy.stats.percentileofscore(gaaArr, player["stats"]["goalsAgainstAverage"])) if player["stats"].get("goalsAgainstAverage") is not None else None,
                        "savePercentage": round(scipy.stats.percentileofscore(svPctArr, player["stats"]["savePercentage"])) if player["stats"].get("savePercentage") is not None else None,
                        "winPercentage": round(scipy.stats.percentileofscore(winPctArr, player["stats"]["winPercentage"])) if player["stats"].get("winPercentage") is not None else None
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
        "gamesPlayedArrDefense": len(gamesPlayedArrDefense),
        "goalsArrDefense": len(goalsArrDefense),
        "assistsArrDefense": len(assistsArrDefense),
        "pmArrDefense": len(pmArrDefense),
        "pimArrDefense": len(pimArrDefense),
        "shotsArrDefense": len(shotsArrDefense),
        "shotPctArrDefense": len(shotPctArrDefense),
        "ppArrDefense": len(ppArrDefense),
        "shArrDefense": len(shArrDefense),
        "esArrDefense": len(esArrDefense),
        "foArrDefense": len(foArrDefense),
        "toiArrDefense": len(toiArrDefense),
        "gaaArr": len(gaaArr),
        "svPctArr": len(svPctArr),
        "winPctArr": len(winPctArr),
        "goaliesGamesPlayedArr": len(goaliesGamesPlayedArr),
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
