import pandas as pd

def print_bets(bets):
    text_bets = ""
    for row in bets:
        text_bets += f"{row.home_team[:3]}-{row.away_team[:3]} \
{row.home_prediction_score}:{row.away_prediction_score} bet={int(row.amount)}\n"

    return text_bets


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
    return repr(df)


def print_leaderboard(leaderboard):
    # print(leaderboard)
    df = pd.DataFrame(leaderboard)
    df.columns = ['Айди', 'Игрок', 'Деньги']
    return df.drop('Айди', axis=1).to_string(index=False)
