from sqlalchemy import String, Integer, Column, Enum, Boolean
from .database import Base
from .enums import TournamentType


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, nullable=False)
    firstname = Column(String, nullable=False)
    surname = Column(String, nullable=True)


class Tournament(Base):
    __tablename__ = "tournaments"

    name = Column(String, primary_key=True, nullable=False)
    type = Column(Enum(TournamentType), nullable=False)
    best_of = Column(Integer)
    total_frames = Column(Integer)


class Matches(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, nullable=False)
    tournament_name = Column(String, nullable=False)
    player1 = Column(Integer, nullable=False)
    player2 = Column(Integer, nullable=False)
    player1_score = Column(Integer)
    player2_score = Column(Integer)


class Results(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, nullable=False)
    tournament_name = Column(String, nullable=False)
    player_id = Column(Integer, nullable=False)
    played = Column(Integer, nullable=False, default=0)
    won = Column(Integer, nullable=False, default=0)
    lost = Column(Integer, nullable=False, default=0)
    drawn = Column(Integer, nullable=False, default=0)
    frames_for = Column(Integer, nullable=False, default=0)
    frames_against = Column(Integer, nullable=False, default=0)


class ScoringSystem(Base):
    __tablename__ = "scoring_system"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    frame_points = Column(Integer, primary_key=True, nullable=False)
    win_points = Column(Integer, primary_key=True, nullable=False)
    default = Column(Boolean, nullable=False)
