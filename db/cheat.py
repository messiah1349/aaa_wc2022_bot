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

# engine.execute('alter table Player add column payment_cnt INTEGER')

with Session(engine) as session:
    # pass
    session.query(Player) \
        .filter(Player.telegram_id == 46340594) \
        .update(
        {'payment_cnt': 1}
    )

    session.query(Player) \
        .filter(Player.telegram_id == 252970915) \
        .update(
        {'payment_cnt': 1}
    )

    session.query(Player) \
        .filter(Player.telegram_id == 271533029) \
        .update(
        {'payment_cnt': 2}
    )

    session.query(Player) \
        .filter(Player.telegram_id == 279075434) \
        .update(
        {'payment_cnt': 1}
    )

    session.query(Player) \
        .filter(Player.telegram_id == 309401434) \
        .update(
        {'payment_cnt': 1}
    )

    session.query(Player) \
        .filter(Player.telegram_id == 530006174) \
        .update(
        {'payment_cnt': 1}
    )

    session.query(Player) \
        .filter(Player.telegram_id == 534584031) \
        .update(
        {'payment_cnt': 1}
    )

    session.query(Player) \
        .filter(Player.telegram_id == 610565754) \
        .update(
        {'payment_cnt': 1}
    )

    session.query(Player) \
        .filter(Player.telegram_id == 1291597799) \
        .update(
        {'payment_cnt': 1}
    )

    session.query(Bet) \
        .filter(Bet.telegram_id == 534584031)\
        .filter(Bet.match_id == 20)\
        .update(
        {'amount': 3000}
    )

    session.commit()

