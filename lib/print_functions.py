import pandas as pd
import prettytable as pt
from markdownTable import markdownTable
import utils as ut


def print_bets(bets):
    table = pt.PrettyTable(['🌍', '⚽', '💰'])
    table.align['🌍'] = 'c'
    table.align['⚽'] = 'c'
    table.align['💰'] = 'r'
    data = []
    text_bets = ""
    for row in bets:
        table.add_row([f"{row.home_team}-{row.away_team}",
                     f'{row.home_prediction_score}:{row.away_prediction_score}',
                     str(int(row.amount))])
    return f'```{table}```'
    # df = pd.DataFrame(data)
    # df.columns = ['матч', 'счет', 'ставк']
    # return markdownTable(df.to_dict(orient='records')).setParams(row_sep='markdown').getMarkdown()


def print_bet(bet):
    return f"`{bet.home_prediction_score}-{bet.away_prediction_score}`; {str(int(bet.amount))}💰"

def split_long_word(word, split_size=3):
    subwords = []
    for i in range(0, len(word), split_size):
        subword = word[i:i+split_size]
        subwords.append(subword)

    return '\n'.join(subwords)

def print_match_bets(bets) -> str:
    table = pt.PrettyTable(['🧑', '⚽', '💰'])
    table.align['🧑'] = 'c'
    table.align['⚽'] = 'c'
    table.align['💰'] = 'r'

    for bet in bets:
        palayer = split_long_word(bet.name, 8)
        table.add_row([f"{palayer}",
                       f'{bet.home_prediction_score}:{bet.away_prediction_score}',
                       str(int(bet.amount))])
    return f'```{table}```'


def print_leaderboard(leaderboard, telegram_id):
    table = pt.PrettyTable(['🧑', '💰'])
    table.align['🧑'] = 'c'
    table.align['💰'] = 'r'

    for user in leaderboard:

        if user.telegram_id == telegram_id:
            player_split = split_long_word(user.name, 12)
            player = '============\n' + player_split + '\n============'
            cnt_of_row = player_split.count('\n')
            money = '======\n' + str(int(user.money)) + '\n'* cnt_of_row + '\n======'
        else:
            player = split_long_word(user.name, 10)
            money = str(int(user.money))

        table.add_row([f"{player}", money])

    return f'```{table}```'



def print_match(match):

    home_team = ut.get_country_name(match.home_team)
    away_team = ut.get_country_name(match.away_team)

    rates = f"{match.home_rate:.2f} - {match.draw_rate:.2f} - {match.away_rate:.2f}" if match.home_rate is not None \
        else "еще не ввнесли"
    score = f"{match.score_home}:{match.score_away}" if match.score_home is not None else "еще не сыграли"

    text = f"""*Команды:* {home_team} - {away_team}\n*Кэфы: * {rates}\n*Счет:* {score}"""

    return text
