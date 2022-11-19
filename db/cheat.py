import os
import sys

from sqlalchemy import create_engine, create_engine, MetaData, Table, Column, Integer, String, DATETIME, Float, insert
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete

from datetime import datetime

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)
import lib.utils as ut

CONFIG_PATH = ROOT_DIR + '/configs/config.yaml'
config = ut.read_config(CONFIG_PATH)
db_path = config['test_bd_path']

data_base_uri = f"sqlite:///{ROOT_DIR}/{db_path}"
engine = create_engine(data_base_uri, echo=True)

from db.tables import Player, Match, Bet

with Session(engine) as session:
    # session.query(Player) \
    #     .filter(Player.telegram_id == 46340594) \
    #     .update(
    #     {'name': 'Мигаев'}
    # )
    # session.commit()

    # session.query(Match).delete()
    # session.commit()
    #
    # session.query(Bet).delete()
    # session.commit()

    session.query(Match) \
        .update(
        {'score_home': None, 'score_away': None, 'outcome': None}
    )
    session.commit()