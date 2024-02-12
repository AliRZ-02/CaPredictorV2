import joblib

from typing import Any
from dataclasses import asdict
from model import Player, PositionEnum, PositionException, SkaterStats, GoalieStats
from constants import SALARY_CAP_VALUE


class Predictor:
    def __init__(self, player: Player, contract_length: int, is_linreg: bool) -> None:
        self.player = player
        self.contract_length = contract_length
        self.is_linreg = is_linreg
    
    def __position_mapper(self, position: str) -> str:
        return {
            PositionEnum.CENTER: "center",
            PositionEnum.GOALIE: "goalies",
            PositionEnum.LEFT_WING: "wings",
            PositionEnum.RIGHT_WING: "wings",
            PositionEnum.DEFENCEMEN: "defencemen"
        }.get(position, None)
    
    def __get_model(self) -> Any:
        position_string = self.__position_mapper(self.player.position)

        if not position_string:
            raise PositionException(self.player.position)
        
        filename = f'models/model_{position_string}.joblib' if not self.is_linreg else f'models/model_linreg_{position_string}.joblib'

        return joblib.load(
            filename=filename
        )
    
    def get_prediction(self) -> dict:
        model = self.__get_model()
        value = None

        if self.player.stats.games_played == 0:
            return {"error": f"Player {self.player.name} has 0 games played"}

        if self.player.position in [PositionEnum.CENTER, PositionEnum.LEFT_WING, PositionEnum.RIGHT_WING]:
            stats : SkaterStats = self.player.stats
            value = model.predict(
                [[
                    stats.goals_82,
                    stats.assists_82,
                    stats.plus_minus_82,
                    stats.shoot_percent,
                    stats.age,
                    stats.start_is_ufa,
                    stats.end_is_ufa,
                    self.contract_length
                ]]
            )
        elif self.player.position == PositionEnum.DEFENCEMEN:
            stats : SkaterStats = self.player.stats
            value = model.predict(
                [[
                    stats.goals_82,
                    stats.assists_82,
                    stats.plus_minus_82,
                    ((stats.penalty_minutes / stats.games_played) * 82),
                    stats.shoot_percent,
                    stats.age,
                    stats.start_is_ufa,
                    stats.end_is_ufa,
                    self.contract_length
                ]]
            )
        else:
            stats : GoalieStats = self.player.stats
            value = model.predict(
                [[
                    (stats.wins / stats.games_played),
                    (stats.shutouts / stats.wins) if stats.wins != 0 else 0,
                    stats.save_percent,
                    stats.goals_against_average,
                    stats.age,
                    stats.start_is_ufa,
                    stats.end_is_ufa,
                    self.contract_length
                ]]
            )

        if value:
            cap_pct = value[0][0] if self.is_linreg else value[0]
            
            return {
                "player": asdict(self.player),
                "contract_length": self.contract_length,
                "value": cap_pct * SALARY_CAP_VALUE
            }
        else:
            return {"error": f"Couldn't predict value for player {self.player.name}"}
