import os
import sys
import telebot
from datetime import datetime
from backend import Backend
import keyboards as kb
import print_functions as pf
from dataclasses import dataclass


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)
import lib.utils as ut

CONFIG_PATH = ROOT_DIR + '/configs/config.yaml'
config = ut.read_config(CONFIG_PATH)
db_path = config['test_bd_path']

# create class with translation of menu for match case usage
menu_names = ut.get_menu_names()

backend = Backend(db_path)

API_TOKEN = os.environ["AAA_BOT_TOKEN"]
bot = telebot.TeleBot(API_TOKEN)

# print('bot started')

@dataclass
class ParsedBet:
    home_score: int
    away_score: int
    amount: float


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_existed_flg = backend.check_user_existence(chat_id).answer

    if user_existed_flg:
        markup = kb.make_welcome_keyboard()
        msg = bot.send_message(chat_id, 'Выберите действие', reply_markup=markup)
    else:
        welcome_not_register_message = """Добро пожаловать в ставочный бот ДПА
Зарегистрируйтесь чтобы начать пользоваться и делать ставки"""
        markup = kb.make_not_registered_welcome_keyboard()
        msg = bot.send_message(chat_id, welcome_not_register_message, reply_markup=markup)

    bot.register_next_step_handler(msg, process_start_menu)


def process_start_menu(message):

    chat_id = message.chat.id
    text = message.text

    match text:
        case menu_names.user_registration:
            msg = bot.send_message(chat_id, "Введите ваше имя")
            bot.register_next_step_handler(msg, process_add_user)
            return
        case menu_names.show_matches:
            matches = backend.get_all_matches()
            markup = kb.make_matches_keyboard(matches)
            bot.send_message(chat_id, "Выбери матч:", reply_markup=markup)
            # handle by process_matches function
            return
        case menu_names.add_match:
            msg = bot.reply_to(message, '''Напиши матч в формате - "Аргентина Ямайка 11 12 15 00"''')
            bot.register_next_step_handler(msg, process_add_match)
            return
        case menu_names.show_leaderboard:
            leaderboard = backend.get_players().answer
            leaderboard = pf.print_leaderboard(leaderboard)
            bot.send_message(chat_id, leaderboard)
            send_welcome(message)
            return
        case menu_names.show_user_bets:
            bets = backend.show_user_bets(chat_id).answer
            bets_text = pf.print_bets(bets) if bets else 'У вас еще нет ставок'
            bot.send_message(chat_id, bets_text)
            send_welcome(message)
            return
        case menu_names.show_current_user_bets:
            clients = backend.get_players().answer
            markup = kb.make_user_bets_keyboard(clients)
            bot.send_message(chat_id, "Выбери игрока:", reply_markup=markup)
            # send_welcome(message)
            return

    markup = kb.make_welcome_keyboard()
    msg = bot.send_message(chat_id, 'Выберите действие', reply_markup=markup)
    bot.register_next_step_handler(msg, process_start_menu)


@bot.callback_query_handler(func=lambda call: bool(call.message) and call.data.startswith('match_id='))
def process_matches(call):
    chat_id = call.message.chat.id
    match_id = int(call.data.split('=')[1])
    game = backend.get_match_by_id(match_id).answer
    text_output = str(game) + '\n\nЧто сделать с этим матчем?'
    markup = kb.make_sub_matches_keyboard()
    msg = bot.send_message(chat_id, text_output, reply_markup=markup)
    bot.register_next_step_handler(msg, process_match, match_id=match_id)


@bot.callback_query_handler(func=lambda call: bool(call.message) and call.data.startswith('telegram_id='))
def process_players(call):
    chat_id = call.message.chat.id
    telegram_id = int(call.data.split('=')[1])
    bets = backend.show_user_bets(telegram_id).answer
    text_output = pf.print_bets(bets)
    bot.send_message(chat_id, text_output)
    send_welcome(call.message)


def process_match(message, match_id):
    chat_id = message.chat.id
    text = message.text
    # print("game = ", text)
    match text:
        case menu_names.make_bet:
            # match = backend.get_match_by_id(match_id).answer
            bet_text = "введте ставку в формате '1 3 500'\nгде первые 2 числа это счет, а последнне - ваша ставка"
            msg = bot.send_message(chat_id, bet_text)
            bot.register_next_step_handler(msg, make_bet, match_id=match_id)
            return
        case menu_names.refresh_score:
            score_text = "Введите счет матча в формате '1 2'\nгде 2 числа это счет"
            msg = bot.send_message(chat_id, score_text)
            bot.register_next_step_handler(msg, process_refresh_score, match_id=match_id)
            return
        case menu_names.refresh_rates:
            rates_text = "Введите кэфы в формате '1.1 2.3 5'\nгде 3 числа это кэфы"
            msg = bot.send_message(chat_id, rates_text)
            bot.register_next_step_handler(msg, process_refresh_rates, match_id=match_id)
            return
        case menu_names.show_match_bets:
            bets = backend.show_match_bets(match_id).answer
            send_text = pf.print_match_bets(bets) if bets else "на этот матч еще никто никто ничего не поставил"
            bot.send_message(chat_id, send_text)
            send_welcome(message)
            return

    send_welcome(message)


def process_refresh_rates(message, match_id):
    chat_id = message.chat.id
    text = message.text
    error_text = "Неправильно ввели!\nВведите кэфы в формате '1.1 2.3 5'\nгде 3 числа это кэфы"

    rates = text.strip().split(' ')
    if len(rates) != 3:
        msg = bot.send_message(chat_id, error_text)
        bot.register_next_step_handler(msg, process_refresh_rates, match_id=match_id)
        return

    try:
        home_rate = float(rates[0])
        draw_rate = float(rates[1])
        away_rate = float(rates[2])
    except ValueError:
        msg = bot.send_message(chat_id, error_text)
        bot.register_next_step_handler(msg, process_refresh_rates, match_id=match_id)
        return

    response = backend.change_rates(match_id, home_rate, draw_rate, away_rate)
    bot.send_message(chat_id, 'Ставки обновлены')

    send_welcome(message)


def process_refresh_score(message, match_id):
    chat_id = message.chat.id
    text = message.text
    error_text = "Неправильно ввели!\nВведите счет матча в формате '1 2'\nгде первые 2 числа это счет"

    score = text.strip().split(' ')
    if len(score) != 2 or not score[0].isnumeric() or not score[1].isnumeric() \
            or int(score[0]) < 0 or int(score[1]) < 0:
        msg = bot.send_message(chat_id, error_text)
        bot.register_next_step_handler(msg, process_refresh_score, match_id=match_id)
        return

    home_score = int(score[0])
    away_score = int(score[1])

    response = backend.change_score(match_id, home_score, away_score)
    if response.status == 0:
        response_money_update = backend.update_client_money()
        if response_money_update.status == 0:
            bot.send_message(chat_id, 'Счет обновлен')
            send_welcome(message)
            return
        else:
            error_message = "Счет обновлен, но произошла проблема при перерасчете денег\nНапишите админу!"
            bot.send_message(chat_id, error_message)
            send_welcome(message)
            return
    else:
        bot.send_message(chat_id, 'Счет почему-то НЕ обновлен')
        send_welcome(message)
        return




def make_bet(message, match_id):
    chat_id = message.chat.id
    text = message.text

    if text == '/start':
        send_welcome(message)
        return

    bet = parse_bet(text)

    if bet:
        current_time = datetime.now()
        resp = backend.add_bet(chat_id, match_id, bet.amount, bet.home_score, bet.away_score, current_time)
        if resp.status == 0:
            resp_score_update = backend.update_client_money()
            if resp_score_update.status == 0:
                msg = bot.send_message(chat_id, "Поздравляем! Вы сделали ставку!")
                send_welcome(msg)
            else:
                error_message = "Вы сделали ставку, но произошла проблема при перерасчете денег\nНапишите админу!"
                msg = bot.send_message(chat_id, error_message)
                send_welcome(msg)
        elif resp.status == 1:
            msg = bot.send_message(chat_id, "вы уже сделали ставку на этот матч!")
            send_welcome(msg)
        elif resp.status == 2:
            msg = bot.send_message(chat_id, "у вас столько денег нет")
            send_welcome(msg)
        elif resp.status == 3:
            msg = bot.send_message(chat_id, 'ставка ниже нуля')
            send_welcome(msg)
        else:
            msg = bot.send_message(chat_id, "что-то пошло не так, попробуйте еще")
            send_welcome(msg)

    else:
        msg = bot.send_message(chat_id,
           """Неправильно ввел!!
введте ставку в формате '1 3 500'
где первые 2 числа это счет, а последнне - ваша ставка
или нажмите /start для выхода в меню"""
           )
        bot.register_next_step_handler(msg, make_bet, match_id=match_id)


def parse_bet(bet_text) -> ParsedBet:
    bet_splitted = bet_text.strip().split(' ')
    try:
        bet = ParsedBet(
            home_score=int(bet_splitted[0]),
            away_score=int(bet_splitted[1]),
            amount=float(bet_splitted[2])
        )
        return bet
    except Exception as e:
        return


def process_add_user(message):
    chat_id = message.chat.id
    text = message.text
    response = backend.add_player(chat_id, text)
    if response.status == 0:
        bot.send_message(chat_id, f'Пользователь {text} добавлен!')
        send_welcome(message)
        return
    else:
        bot.send_message(chat_id, response.answer)
        send_welcome(message)
        return


def process_add_match(message):
        chat_id = message.chat.id
        text = message.text
        splitted_text = text.split(" ")
        if len(splitted_text) != 6:
            msg = bot.reply_to(message,
                    '''Неверно указал!\nНапиши матч в формате - "Аргентина Ямайка 11 12 15 00"''')
            bot.register_next_step_handler(msg, process_add_match)
            return

        home_team = splitted_text[0]
        away_team = splitted_text[1]
        mth = splitted_text[2]
        day = splitted_text[3]
        hour = splitted_text[4]
        minute = splitted_text[5]

        try:
            mth = int(mth)
            day = int(day)
            hour = int(hour)
            minute = int(minute)
            match_date = datetime(2022, mth, day, hour, minute)
        except ValueError:
            msg = bot.reply_to(message,
             '''Неверно указал!\nнапиши матч в формате - "Аргентина Ямайка 11 12 15 00"\nИ следи за чиселками даты!''')
            bot.register_next_step_handler(msg, process_add_match)
            return

        response = backend.add_match(home_team, away_team, match_date)
        if response.status == 1:
            msg = bot.reply_to(message, 'такой матч уже есть')
            bot.register_next_step_handler(msg, process_add_match)
            return

        elif response.status == 0:
            msg = bot.send_message(chat_id, 'Матч добавлен!')
            send_welcome(msg)
            return

        send_welcome(msg)


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()
bot.infinity_polling(none_stop=True)


