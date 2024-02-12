from dataclasses import dataclass
from enum import Enum


class PositionEnum(Enum):
    CENTER = 'C'
    GOALIE = 'G'
    LEFT_WING = 'L'
    RIGHT_WING = 'R'
    DEFENCEMEN = 'D'


class PositionException(Exception):
    def __init__(self, position: PositionEnum, message: str = "Invalid Position") -> None:
        self.message = f'The position {str(position)} is invalid' if not message else message
        super().__init__(self.message)


@dataclass
class PlayerStats:
    games_played: float
    age: float
    start_is_ufa: bool
    end_is_ufa: bool


@dataclass
class SkaterStats(PlayerStats):
    goals_82: float
    assists_82: float
    plus_minus_82: float
    penalty_minutes: float
    shoot_percent: float
    age: float


@dataclass
class GoalieStats(PlayerStats):
    games_started: float
    wins: float
    losses: float
    shutouts: float
    save_percent: float
    goals_against_average: float


@dataclass
class Player:
    name: str
    stats: PlayerStats
    position: PositionEnum
