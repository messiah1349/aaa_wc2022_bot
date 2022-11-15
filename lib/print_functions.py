import pandas as pd
from tabulate import tabulate
from markdownTable import markdownTable


def print_bets(bets):
    data = []
    text_bets = ""
    for row in bets:
        data.append([f"{row.home_team[:3]}-{row.away_team[:3]}",
                     f'{row.home_prediction_score}:{row.away_prediction_score}',
                     str(int(row.amount))])
        # text_bets += f"{row.home_team[:3]}-{row.away_team[:3]} \
# {row.home_prediction_score}:{row.away_prediction_score} bet={int(row.amount)}\n"
    df = pd.DataFrame(data)
    df.columns = ['матч', 'счет', 'ставк']
    return markdownTable(df.to_dict(orient='records')).setParams(row_sep='markdown').getMarkdown()


def print_bet(bet):
    return f"{bet.home_prediction_score} - {bet.away_prediction_score}, {bet.amount}"


def print_match_bets(bets) -> str:
    # output_text = ""
    # for bet in bets:
        # row = f"{bet.name:10} {bet.home_prediction_score}-{bet.away_prediction_score} {int(bet.amount):5d}руб"
        # row = bet.name.rjust(10) + str(bet.home_prediction_score) + '-' + str(bet.away_prediction_score) + \
        #       ' ' + str(int(bet.amount)).rjust(5) + 'руб'
        # ?output_text = output_text + '\n' + row

    df = pd.DataFrame(bets)
    df.columns = ['игрок', 'счет1', 'счет2', 'ставка', 'дата']
    df['дата'] = df['дата'].dt.strftime('%m/%d')
    df = df.drop('дата', axis=1)
    return markdownTable(df.to_dict(orient='records')).setParams(row_sep='markdown').getMarkdown()


def print_leaderboard(leaderboard):
    # print(leaderboard)
    df = pd.DataFrame(leaderboard)
    df.columns = ['Айди', 'Игрок', 'Деньги']
    df = df.drop('Айди', axis=1)
    # return df.drop('Айди', axis=1).to_string(index=False)
    # data = [[x[1], x[2]] for x in leaderboard]
    # tab_table = tabulate(data, headers=['Игрок', 'Деньги'])
    # print(tab_table)
    # return tab_table

    # text = """* bets *"""
    # for user in leaderboard:
    #     text += f"""```````n{user[1]}:   """
    # print(df.to_dict(orient='records'))

    return markdownTable(df.to_dict(orient='records')).setParams(row_sep='markdown').getMarkdown()


