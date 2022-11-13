import os
import sys

from sqlalchemy import create_engine, create_engine, MetaData, Table, Column, Integer, String, DATETIME, Float, insert
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)
import lib.utils as ut


Base = declarative_base()


class Match(Base):

    __tablename__ = 'match'
    id = Column(Integer, primary_key=True)
    home_team = Column(String)
    away_team = Column(String)
    match_time = Column(DATETIME)
    score_home = Column(Integer)
    score_away = Column(Integer)
    outcome = Column(String)
    home_rate = Column(Float)
    draw_rate = Column(Float)
    away_rate = Column(Float)

    def __repr__(self):
        rates = f"{self.home_rate:.2f} - {self.draw_rate:.2f} - {self.away_rate:.2f}" if self.home_rate is not None \
            else "not available yet"
        score = f"{self.score_home} - {self.score_away}" if self.score_home is not None else "not available yet"
        repr = f"""teams: {self.home_team} - {self.away_team}\nrates: {rates}\nscore: {score}"""
        return repr


class Player(Base):

    __tablename__ = 'player'

    telegram_id = Column(Integer, primary_key=True)
    name = Column(String)
    money = Column(Float)


class Bet(Base):

    __tablename__ = 'bet'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    match_id = Column(Integer)
    amount = Column(Float)
    prediction_outcome = Column(String)
    home_prediction_score = Column(Integer)
    away_prediction_score = Column(Integer)
    date = Column(DATETIME)


if __name__ == '__main__':

    CONFIG_PATH = ROOT_DIR + '/configs/config.yaml'
    config = ut.read_config(CONFIG_PATH)
    bd_path = config['test_bd_path']

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{ROOT_DIR}/{bd_path}"

    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)
