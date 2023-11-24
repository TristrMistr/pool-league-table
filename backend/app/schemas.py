from pydantic import BaseModel, validator, root_validator
from typing import Optional
from .enums import TournamentType


class Tournament(BaseModel):
    name: str
    people: list[str]
    type: TournamentType
    best_of: Optional[int]
    total_frames: Optional[int]

    @root_validator()
    def validate_type(cls, values):
        game_type = values.get("type")
        best_of = values.get("best_of")
        total_frames = values.get("total_frames")

        if game_type == TournamentType.BEST_OF:
            if best_of is None:
                raise ValueError("best_of field cant be empty when the tournemant is a best of type")
        elif game_type == TournamentType.PLAY_ALL:
            if total_frames is None:
                raise ValueError("total_frames field cant be empty when the tournemant is a play all type")
        return values

    @validator("best_of")
    def test_bo_not_negative(cls, value):
        if value is not None:
            if value < 0:
                raise ValueError("best_of field can't be negative")
        return value

    @validator("total_frames")
    def test_total_not_negative(cls, value):
        if value is not None:
            if value < 0:
                raise ValueError("best_of field can't be negative")
        return value


class Person(BaseModel):
    id: Optional[str]
    firstname: str
    surname: str


class Match(BaseModel):
    id: Optional[int]
    tournament_name: str
    player1: int
    player2: int
    player1_score: Optional[int]
    player2_score: Optional[int]


class Result(BaseModel):
    player_name: str
    played: int = 0
    won: int = 0
    lost: int = 0
    drawn: int = 0
    frames_for: int = 0
    frames_against: int = 0
    points: int = 0