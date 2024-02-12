from async_lru import alru_cache
from aiohttp import ClientSession
from urllib.parse import urlencode
from model import SkaterStats, GoalieStats, PositionEnum
from datetime import datetime
from utils import convert_time_to_float


@alru_cache
async def request_players() -> list[str]:
    async with ClientSession() as session:
        ALL_PLAYERS_URL = "https://search.d3.nhle.com/api/v1/search/player"
        params = {
            "culture": "en-us",
            "limit": 3000,
            "q": "*",
            "active": True
        }

        search_url = f'{ALL_PLAYERS_URL}?{urlencode(params)}'
        async with session.get(search_url) as resp:
            return await resp.json()


@alru_cache
async def request_players_by_id(player_id: str) -> dict:
    async with ClientSession() as session:
        search_url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
        async with session.get(search_url) as resp:
            return await resp.json()


@alru_cache
async def get_player_stats(player_id: str):
    data = await request_players_by_id(player_id)
    
    position = data.get("position", None)
    if not position or not isinstance(position, str):
        return None
    
    season_stats = data.get("seasonTotals", [])
    if not season_stats:
        return None
    
    last_season = [season for season in season_stats if season.get("gameTypeId", 0) == 2][-1]
    birth_year = datetime.strptime(data.get("birthDate"), r"%Y-%m-%d").year
    last_year = last_season.get("season", "2024") % 10_000
    age = last_year - birth_year

    if not last_season.get("gamesPlayed", 0):
        return None
                
    if position == "G":
        if not last_season.get('timeOnIce', 0):
            return None
    
        if not last_season.get('shotsAgainst', 0):
            return None
    
        return GoalieStats(
            games_played = last_season.get("gamesPlayed"),
            age = age,
            start_is_ufa = True if age > 27 else False,
            end_is_ufa = True,
            games_started = last_season.get("gamesStarted"),
            wins = last_season.get("wins"),
            losses = last_season.get("losses") + last_season.get("otLosses"),
            shutouts = last_season.get("shutouts"),
            save_percent = 1 - (last_season.get('goalsAgainst') / last_season.get('shotsAgainst')),
            goals_against_average = last_season.get('goalsAgainst') / (convert_time_to_float(last_season.get('timeOnIce')) / 60)
        )
    else:
        if not last_season.get('shots', 0):
            return None
        
        return SkaterStats(
            games_played = last_season.get('gamesPlayed'),
            age = age,
            start_is_ufa = True if age > 27 else False,
            end_is_ufa = True,
            penalty_minutes = last_season.get('pim'),
            goals_82 = (last_season.get('goals') / last_season.get('gamesPlayed')) * 82,
            assists_82 = (last_season.get('assists') / last_season.get('gamesPlayed')) * 82,
            plus_minus_82 = (last_season.get('plusMinus') / last_season.get('gamesPlayed')) * 82,
            shoot_percent = last_season.get('goals') / last_season.get('shots')
        )


@alru_cache
async def get_player_position(player_id: str) -> PositionEnum:
    data = await request_players_by_id(player_id)

    return PositionEnum(data.get("position", None))
