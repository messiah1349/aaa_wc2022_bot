import prettytable as pt
import utils as ut

emoji_good = '✅'
emoji_bad = '❌'
def print_bets(bets):
    table = pt.PrettyTable(['🌍', '⚽', '💰'])
    table.align['🌍'] = 'c'
    table.align['⚽'] = 'c'
    table.align['💰'] = 'r'

    for row in bets:
        money = str(int(row.amount))
        if row.winning == 0:
            money = emoji_bad + money
        elif row.winning == 1:
            money = emoji_good + money
        elif row.winning == 2:
            money = emoji_good + emoji_good + money

        table.add_row([f"{row.home_team}-{row.away_team}",
                     f'{row.home_prediction_score}:{row.away_prediction_score}',
                     money])
    return f'```{table}```'


def print_bet(bet):
    return f"`{bet.home_prediction_score}-{bet.away_prediction_score}`; {str(int(bet.amount))}💰"


def split_long_word(word, split_size=3):
    sub_words = []
    for i in range(0, len(word), split_size):
        sub_word = word[i:i+split_size]
        sub_words.append(sub_word)

    return '\n'.join(sub_words)

def print_match_bets(bets) -> str:
    table = pt.PrettyTable(['🧑', '⚽', '💰'])
    table.align['🧑'] = 'c'
    table.align['⚽'] = 'c'
    table.align['💰'] = 'r'

    for row in bets:

        money = str(int(row.amount))
        if row.winning == 0:
            money = emoji_bad + money
        elif row.winning == 1:
            money = emoji_good + money
        elif row.winning == 2:
            money = emoji_good + emoji_good + money

        player = split_long_word(row.name, 8)
        table.add_row([f"{player}",
                       f'{row.home_prediction_score}:{row.away_prediction_score}',
                       money])
    return f'```{table}```'


def print_leaderboard(leaderboard, telegram_id):
    table = pt.PrettyTable(['🧑', '💰'])
    table.align['🧑'] = 'c'
    table.align['💰'] = 'r'

    for user in leaderboard:

        coins = '🪙' * user.payment_cnt if user.payment_cnt else ''

        if user.telegram_id == telegram_id:
            player_split = split_long_word(user.name, 12)
            player = '============\n' + player_split + '\n============'
            cnt_of_row = player_split.count('\n')
            money = '======\n' + coins + str(int(user.money)) + '\n'* cnt_of_row + '\n======'
        else:
            player = split_long_word(user.name, 10)
            money = coins + str(int(user.money))

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
