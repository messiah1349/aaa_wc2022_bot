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

from lib.backend import Backend, TableProcessor, PlayerProcessor, MatchProcessor, Response
from db.tables import Player, Match, Bet

back = Backend(db_path)


with Session(engine) as session:

    session.query(Player).delete()
    session.commit()

    session.query(Match).delete()
    session.commit()

    session.query(Bet).delete()
    session.commit()

    print('\n\n\ngggggg\n\n\n')
    assert session.query(Player).count() == 0 and session.query(Match).count() == 0
    print('\n\n\nwwwwwww\n\n\n')
    res1 = back.add_player(700, 'ivan')
    print(res1)
    assert res1 == Response(status=0, answer='user added')
    res2 = back.add_player(701, 'ivan')
    assert res2 == Response(status=1, answer='user name has already existed')
    res3 = back.add_player(700, 'ivan2')
    assert res3 == Response(status=2, answer='telegram user has already existed')
    res4 = back.add_player(800, 'anton')
    assert res4 == Response(status=0, answer='user added')

    res = session.query(Player).count()
    assert res == 2

    m1 = back.add_match('russia', 'urugvay', datetime(2022, 11, 8, 10, 20, 55))
    m2 = back.add_match('russia', 'nemcy', datetime(2022, 12, 8, 10, 20, 55))
    assert session.query(Match).count() == 2
    m2 = back.add_match('russia', 'nemcy', datetime(2022, 11, 8, 10, 20, 55))
    assert session.query(Match).count() == 2

    back.change_score(1, 1, 2)
    m3 = session.execute(session.query(Match).filter(Match.score_home == 1)).first()
    # assert str(m3) == "(russia - urugvay, score - 1 - 2,)"

    back.add_bet(700, 1, 300, 4, 3, datetime(2022, 11, 8, 10, 20, 55))
    print("cnt ==== ", session.query(Bet).count())
    assert session.query(Bet).count() == 1
    back.add_bet(700, 1, 200, 4, 3, datetime(2022, 11, 8, 10, 20, 55))
    assert session.query(Bet).filter(Bet.is_deleted == 0).count() == 1
    back.add_bet(700, 2, 205, 1, 1, datetime(2022, 11, 8, 10, 20, 57))
    assert session.query(Bet).filter(Bet.is_deleted == 0).count() == 2

    back.add_bet(800, 1, 700, 2, 2, datetime(2022, 11, 8, 10, 20, 55))

    m4 = back.get_match_by_id(2)
    # assert str(m4.answer) == "russia - nemcy, score - None - None"

    bets = back.show_user_bets(700).answer
    for row in bets:
        print(f"{row.home_team[:3]}-{row.away_team[:3]} {row.home_prediction_score}:{row.away_prediction_score} bet={row.amount}")

    bets = back.show_match_bets(1).answer

    # for bet in bets:
    #     print(bet)

    pp = PlayerProcessor(engine)
    amount = pp.get_amount_by_user(700)

    all_clients = back.get_players().answer
    print(all_clients)

    all_money_resp = back.update_client_money()
    print(all_money_resp)

    all_clients = back.get_players().answer
    print(all_clients)

    m4 = back.get_match_by_id(2)
    print(m4.answer.match_time)

    # matches = back.get_all_matches()
    # # print(matches)
    #
    # for row in matches:
    #     print(row.home_team, row.away_team, str(row))
