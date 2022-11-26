import os
import sys
from datetime import datetime
import pytz

from sqlalchemy import create_engine, MetaData, Table, insert, func, case, and_, or_, update, select
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import Session
from typing import Any

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)
import lib.utils as ut
from db.tables import Player, Match, Bet

CONFIG_PATH = ROOT_DIR + '/configs/config.yaml'
config = ut.read_config(CONFIG_PATH)

INITIAL_USER_MONEY = config['initial_user_money']
PREDICTED_SCORE_COEFF = config['predicted_score_coeff']

from dataclasses import dataclass


def calculate_outcome(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return 'W1'
    elif home_score == away_score:
        return 'DD'
    else:
        return 'W2'


@dataclass
class Response:
    status: int
    answer: Any


class TableProcessor:

    def __init__(self, engine):
        self._engine = engine

    def _get_table(self, table_name: str) -> Table:
        meta_data = MetaData(bind=self._engine)
        meta_data.reflect()
        table = meta_data.tables[table_name]
        return table

    def _insert_into_table(self, table_model, data: dict):
        ins_command = insert(table_model).values(**data)

        with Session(self._engine) as session:
            session.execute(ins_command)
            session.commit()

    @staticmethod
    def _return_query_execution_result(query_result):
        d, a = {}, []
        for row_proxy in query_result:
            # row_proxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in row_proxy.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(d)
        return a

    def _get_max_value_of_column(self, table_model, column_name):

        with Session(self._engine) as session:
            res = session.execute(func.max(getattr(table_model, column_name)))
            res = res.first()[0]
            if not res:
                res = 0
            return res

    def _check_existence(self, table_model, column_name, value):
        with Session(self._engine) as session:
            res = session.query(table_model).filter(getattr(table_model, column_name) == value)
            res = res.count()
            return bool(res)

    def _get_all_data_from_table(self, table_model):
        with Session(self._engine) as session:
            res = session.query(table_model)
            return res

    def _get_data_by_id(self, table_model, id_value: int, id_column='id'):
        with Session(self._engine) as session:
            query = session.query(table_model).filter(getattr(table_model, id_column) == id_value)
            res = session.execute(query)
            return res.fetchone()[0]


class PlayerProcessor(TableProcessor):

    def __init__(self, engine):
        super().__init__(engine)
        self.table_model = Player

    def _check_existence_name(self, value: str) -> bool:
        return self._check_existence(self.table_model, 'name', value)

    def _check_existence_telegram_id(self, value: int) -> bool:
        return self._check_existence(self.table_model, 'telegram_id', value)

    def get_players(self) -> Response:

        with Session(self._engine) as session:

            query = session.query(self.table_model).with_entities(
                     getattr(self.table_model, 'telegram_id'),
                    getattr(self.table_model, 'name'),
                    getattr(self.table_model, 'money'),
                    getattr(self.table_model, 'payment_cnt')
            ).order_by(getattr(self.table_model, 'money').desc(), getattr(self.table_model, 'name'))

            res = session.execute(query).fetchall()

        return Response(0, res)

    def add_player(self, telegram_id: int, player_name: str) -> Response:

        if self._check_existence_name(player_name):
            return Response(1, 'user name has already existed')

        if self._check_existence_telegram_id(telegram_id):
            return Response(2, 'telegram user has already existed')

        data = {
            'telegram_id': telegram_id,
            'name': player_name,
            'money': INITIAL_USER_MONEY
        }

        self._insert_into_table(self.table_model, data)

        return Response(0, 'user added')

    def get_player_by_id(self, telegram_id: int) -> Response:
        player_name = self._get_data_by_id(self.table_model, telegram_id, 'telegram_id').name
        return Response(0, player_name)

    def get_amount_by_user(self, telegram_id: int) -> float:
        return self._get_data_by_id(self.table_model, telegram_id, 'telegram_id').money

    def check_user_is_register(self, telegram_id: int) -> Response:
        exist_flg = self._check_existence_telegram_id(telegram_id)
        return Response(0, exist_flg)

    def update_money(self) -> Response:

        mixed_table_processor = MixedTableProcessor(self._engine)

        try:
            with Session(self._engine) as session:

                # inside this query we can calculate current money for every player
                current_money_query = mixed_table_processor.calculate_money_for_players()

                # join result from getting subquery and update money column at Player Table
                query = self.table_model.__table__.update().values(
                    money=select(coalesce(current_money_query.c.current_money, INITIAL_USER_MONEY))\
                                .where(getattr(self.table_model, 'telegram_id') == current_money_query.c.telegram_id)\
                                .scalar_subquery()
                )
                session.execute(query)
                session.commit()

                return Response(0, 'money_updated')
        except Exception as e:
            print(e)
            return Response(1, e)


class MatchProcessor(TableProcessor):

    def __init__(self, engine):
        super().__init__(engine)
        self.table_model = Match

    def _generate_id(self) -> int:
        return self._get_max_value_of_column(self.table_model, 'id') + 1

    def _get_match_query(self, match_id):
        with Session(self._engine) as session:
            query = session.query(self.table_model)\
                .filter(getattr(self.table_model, 'id') == match_id)

            return query

    def _get_mathc_query_by_team_names(self, home_team: str, away_team: str):
        with Session(self._engine) as session:
            query = session.query(self.table_model) \
                .filter(getattr(self.table_model, 'home_team') == home_team)\
                .filter(getattr(self.table_model, 'away_team') == away_team)\

            return query

    def _get_match_row(self, home_team: str, away_team: str):
        with Session(self._engine) as session:
            return session.execute(self._get_match_query(home_team, away_team))

    def add_match(self, home_team: str, away_team: str, match_time: datetime) -> Response:

        if self._get_mathc_query_by_team_names(home_team, away_team).count() > 0:
            return Response(1, 'match has already existed')

        match_id = self._generate_id()

        insert_data = {
            'id': match_id,
            'home_team': home_team,
            'away_team': away_team,
            'match_time': match_time,
            'score_home': None,
            'score_away': None
        }

        self._insert_into_table(self.table_model, insert_data)

        return Response(0, 'match added')

    def delete_match(self, home_team: str, away_team: str) -> Response:
        with Session(self._engine) as session:
            session.execute(session.query(self.table_model)\
                                   .filter(self._get_match_query(home_team, away_team))
                                   .delete()
                            )

            return Response(1, 'match deleted')

    def change_score(self, match_id: int, score_home: int, score_away: int):

        if not self._get_match_query(match_id).count():
            return Response(1, 'match has not existed yet')

        outcome = calculate_outcome(score_home, score_away)

        with Session(self._engine) as session:
            session.query(self.table_model)\
                .filter(getattr(self.table_model, 'id') == match_id)\
                .update(
                    {'score_away': score_away, 'score_home': score_home, 'outcome': outcome}
                )
            session.commit()

        mixed_table_processor = MixedTableProcessor(self._engine)
        players_results = mixed_table_processor.calculate_winnings_for_match(match_id)

        return Response(0, players_results)

    def change_rates(self, match_id: int, home_rate: float, draw_rate: float, away_rate: float) -> Response:

        if not self._get_match_query(match_id).count():
            return Response(1, 'match has not existed yet')

        with Session(self._engine) as session:
            session.query(self.table_model)\
                .filter(getattr(self.table_model, 'id') == match_id)\
                .update(
                    {'home_rate': home_rate, 'draw_rate': draw_rate, 'away_rate': away_rate}
                )
            session.commit()

        return Response(0, 'rates updated')

    def change_team_names(self, match_id: int, home_team: str, away_team: str):

        if not self._get_match_query(match_id).count():
            return Response(1, 'match has not existed yet')

        with Session(self._engine) as session:
            session.query(self.table_model)\
                .filter(getattr(self.table_model, 'id') == match_id)\
                .update(
                    {'home_team': home_team, 'away_team': away_team}
                )
            session.commit()

        return Response(0, 'rates updated')

    def get_all_matches(self):
        return self._get_all_data_from_table(self.table_model)

    def get_match_by_id(self, id_value):
        response = Response(0, self._get_data_by_id(self.table_model, id_value))
        return response


class BetProcessor(TableProcessor):

    def __init__(self, engine):
        super().__init__(engine)
        self.table_model = Bet

    def _generate_id(self) -> int:
        return self._get_max_value_of_column(self.table_model, 'id') + 1

    def _get_bet_query(self, telegram_id: int, match_id: int):
        with Session(self._engine) as session:
            query = session.query(self.table_model)\
                .filter(getattr(self.table_model, 'telegram_id') == telegram_id) \
                .filter(getattr(self.table_model, 'match_id') == match_id)\
                .filter(getattr(self.table_model, 'is_deleted') == 0)

            return query

    def _mark_bets_as_deleted(self, telegram_id: int, match_id: int) -> None:
        with Session(self._engine) as session:
            session.query(self.table_model) \
                .filter(getattr(self.table_model, 'telegram_id') == telegram_id) \
                .filter(getattr(self.table_model, 'match_id') == match_id) \
                .update(
                    {'is_deleted': 1}
                )
            session.commit()

    def get_bet_by_player_and_client_id(self, telegram_id: int, match_id: int):
        with Session(self._engine) as session:
            query = self._get_bet_query(telegram_id, match_id)
            res = session.execute(query).fetchone()
            return Response(0, res)

    def add_bet(self, telegram_id: int, match_id: int, amount: float, home_prediction_score: int,
                away_prediction_score: int, bet_date: datetime) \
            -> Response:

        player_processor = PlayerProcessor(self._engine)
        user_amount = player_processor.get_amount_by_user(telegram_id)

        if amount > user_amount:
            return Response(2, 'not enough money')

        if amount < 0:
            return Response(3, 'negative value')

        match_processor = MatchProcessor(self._engine)
        match_time = match_processor.get_match_by_id(match_id).answer.match_time
        match_time = pytz.timezone('Europe/Moscow').localize(match_time)
        # bet_date = pytz.timezone('Europe/Moscow').localize(bet_date)

        if bet_date > match_time:
            return Response(4, 'late bet')

        if self._get_bet_query(telegram_id, match_id).count() > 0:
            self._mark_bets_as_deleted(telegram_id, match_id)
            _ = player_processor.update_money()

        bet_id = self._generate_id()

        outcome = calculate_outcome(home_prediction_score, away_prediction_score)

        insert_data = {
            'id': bet_id,
            'telegram_id': telegram_id,
            'match_id': match_id,
            'amount': amount,
            'home_prediction_score': home_prediction_score,
            'away_prediction_score': away_prediction_score,
            'prediction_outcome': outcome,
            'date': bet_date,
            'is_deleted': 0
        }

        self._insert_into_table(self.table_model, insert_data)

        return Response(0, 'bet added')


class MixedTableProcessor:
    def __init__(self, engine):
        self._engine = engine

    def _get_full_bet_info(self):

        with Session(self._engine) as session:
            query = session.query(Bet, Match, Player) \
                .filter(Bet.is_deleted == 0) \
                .filter(Bet.match_id == Match.id) \
                .filter(Bet.telegram_id == Player.telegram_id) \
                .order_by(Match.match_time) \
                .with_entities(Match.home_team, Match.away_team, Bet.home_prediction_score, Bet.away_prediction_score,
                       Bet.amount, Bet.date, Player.telegram_id, Match.id.label('match_id'), Player.name,
                       case(
                           (Match.outcome == None, -1),
                           (and_(
                               (Bet.home_prediction_score == Match.score_home),
                               (Bet.away_prediction_score == Match.score_away)
                           ), 2),
                           (Bet.prediction_outcome == Match.outcome, 1),
                           else_=0
                       ).label('winning')
                    )

            return query


    def get_user_bets(self, telegram_id: int) -> Response:
        try:
            with Session(self._engine) as session:

                bet_info = self._get_full_bet_info().subquery()
                query = session.query(bet_info).filter(bet_info.c.telegram_id == telegram_id)

                res = session.execute(query).fetchall()
                return Response(0, res)
        except Exception as e:
            print(e)
            return Response(1, "something was wrong")

    def get_match_bets(self, match_id: int) -> Response:
        try:
            with Session(self._engine) as session:
                # query = session.query(Bet, Player)\
                #     .filter(Bet.match_id == match_id) \
                #     .filter(Bet.telegram_id == Player.telegram_id) \
                #     .filter(Bet.is_deleted == 0)\
                #     .order_by(Bet.date)\
                #     .with_entities(Player.name, Bet.home_prediction_score, Bet.away_prediction_score,
                #                    Bet.amount, Bet.date)
                bet_info = self._get_full_bet_info().subquery()
                query = session.query(bet_info).filter(bet_info.c.match_id == match_id)

                res = session.execute(query).fetchall()
                return Response(0, res)
        except Exception as e:
            return Response(1, "something was wrong")

    def _join_match_and_bets(self):
        with Session(self._engine) as session:

            query = session.query(Match, Bet)\
                .filter(Bet.match_id == Match.id) \
                .filter(Bet.is_deleted == 0)\
                .with_entities(
                    Bet.telegram_id.label('telegram_id'),
                    Match.id.label('match_id'),
                    case(
                        (Bet.prediction_outcome != Match.outcome, 0),
                        (Match.outcome == 'W1', Bet.amount * Match.home_rate),
                        (Match.outcome == 'DD', Bet.amount * Match.draw_rate),
                        (Match.outcome == 'W2', Bet.amount * Match.away_rate),
                        else_=0
                    ).label('amount_outcome'),
                    case(
                        (and_(
                            (Bet.home_prediction_score == Match.score_home),
                            (Bet.away_prediction_score == Match.score_away)
                        ),
                         Bet.amount * PREDICTED_SCORE_COEFF
                        ),
                        else_=0
                    ).label('predicted_score_outcome'),
                    Bet.amount.label('total_bet_amount')
                )

            return query

    def calculate_money_for_players(self):
        with Session(self._engine) as session:

            pre_aggregate_subquery = self._join_match_and_bets().subquery()
            aggregate_subquery = session.query(pre_aggregate_subquery)\
                .with_entities(
                    pre_aggregate_subquery.c.telegram_id,
                    coalesce(func.sum(pre_aggregate_subquery.c.amount_outcome), 0).label('amount_outcome'),
                    coalesce(func.sum(pre_aggregate_subquery.c.predicted_score_outcome), 0)\
                        .label('predicted_score_outcome'),
                    coalesce(func.sum(pre_aggregate_subquery.c.total_bet_amount), 0).label('total_bet_amount')
                )\
                .group_by(pre_aggregate_subquery.c.telegram_id).subquery()

            client_money_query = session.query(Player)\
                .join(aggregate_subquery, Player.telegram_id == aggregate_subquery.c.telegram_id, isouter=True) \
                .with_entities(
                    Player.telegram_id,
                    coalesce(
                         INITIAL_USER_MONEY * coalesce(Player.payment_cnt, 1) +
                         aggregate_subquery.c.amount_outcome +
                         aggregate_subquery.c.predicted_score_outcome -
                         aggregate_subquery.c.total_bet_amount,
                      INITIAL_USER_MONEY * coalesce(Player.payment_cnt, 1)
                    ).label('current_money')
                )\
                .subquery()

            return client_money_query

    def calculate_winnings_for_match(self, match_id: int):
        with Session(self._engine) as session:

            all_matches = self._join_match_and_bets().subquery()
            current_match = session.query(all_matches)\
                .filter(all_matches.c.match_id==match_id)

            total_query = current_match.with_entities(
                all_matches.c.telegram_id.label('telegram_id'),
                (all_matches.c.amount_outcome +
                all_matches.c.predicted_score_outcome).label('winning'),
                all_matches.c.total_bet_amount.label('bet_amount')
            )
            res = session.execute(total_query).fetchall()
            return res


class Backend:

    def __init__(self, db_path: str):
        data_base_uri = f"sqlite:///{ROOT_DIR}/{db_path}"
        self._engine = create_engine(data_base_uri, echo=False, connect_args={"check_same_thread": False})

    def add_player(self, telegram_id: int, player_name: str):
        client_processor = PlayerProcessor(self._engine)
        response = client_processor.add_player(telegram_id, player_name)
        return response

    def check_user_existence(self, telegram_id):
        client_processor = PlayerProcessor(self._engine)
        response = client_processor.check_user_is_register(telegram_id)
        return response

    def get_players(self) -> Response:
        client_processor = PlayerProcessor(self._engine)
        response = client_processor.get_players()
        return response

    def get_player_by_id(self, telegram_id: int):
        client_processor = PlayerProcessor(self._engine)
        response = client_processor.get_player_by_id(telegram_id)
        return response

    def add_match(self, home_team: str, away_team: str, match_time: datetime):
        match_processor = MatchProcessor(self._engine)
        response = match_processor.add_match(home_team, away_team, match_time)
        return response

    def change_score(self, match_id: int, score_home: int, score_away: int):
        match_processor = MatchProcessor(self._engine)
        response = match_processor.change_score(match_id, score_home, score_away)
        return response

    def change_rates(self, match_id: int, home_rate: float, draw_rate: float, away_rate: float):
        match_processor = MatchProcessor(self._engine)
        response = match_processor.change_rates(match_id, home_rate, draw_rate, away_rate)
        return response

    def change_team_names(self, match_id: int, home_team: str, away_team: str) -> Response:
        match_processor = MatchProcessor(self._engine)
        response = match_processor.change_team_names(match_id, home_team, away_team)
        return response

    def add_bet(self, telegram_id: int, match_id: int, amount: float, home_prediction_score: int,
                away_prediction_score: int, bet_date: datetime) -> Response:
        bet_processor = BetProcessor(self._engine)
        response = bet_processor.add_bet(telegram_id, match_id, amount, home_prediction_score,
                                         away_prediction_score, bet_date)

        return response

    def get_bet_by_player_and_client_id(self, telegram_id: int, match_id: int):
        bet_processor = BetProcessor(self._engine)
        response = bet_processor.get_bet_by_player_and_client_id(telegram_id, match_id)
        return response

    def show_user_bets(self, telegram_id):
        mixed_table_processor = MixedTableProcessor(self._engine)
        resp = mixed_table_processor.get_user_bets(telegram_id)
        return resp

    def show_match_bets(self, match_id):
        mixed_table_processor = MixedTableProcessor(self._engine)
        resp = mixed_table_processor.get_match_bets(match_id)
        return resp

    def get_all_matches(self):
        match_processor = MatchProcessor(self._engine)
        response = match_processor.get_all_matches()
        return response

    def get_match_by_id(self, id_value):
        match_processor = MatchProcessor(self._engine)
        response = match_processor.get_match_by_id(id_value)
        return response

    def update_client_money(self):
        player_processor = PlayerProcessor(self._engine)
        resp = player_processor.update_money()
        return resp
