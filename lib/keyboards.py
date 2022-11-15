import os
import sys
from telebot import types

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)

import lib.utils as ut
menu_names = ut.get_menu_names()
admin_lists = ut.get_admin_list()


def make_not_registered_welcome_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(menu_names.user_registration)
    return markup


def make_welcome_keyboard(telegram_id: int):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(menu_names.show_matches)
    markup.add(menu_names.show_leaderboard)
    markup.add(menu_names.show_user_bets)
    markup.add(menu_names.show_current_user_bets)
    markup.add(menu_names.show_finished_matches)

    if telegram_id in admin_lists:
        markup.add(menu_names.add_match)

    return markup


def make_matches_keyboard(matches):
    markup = types.InlineKeyboardMarkup()
    for match in matches:
        home_flag = ut.get_flag_emoji(match.home_team)
        away_flag = ut.get_flag_emoji(match.away_team)
        button_team_text = f"{home_flag}{match.home_team.upper()} - {match.away_team.upper()}{away_flag}   "
        button_time_text = f"{match.match_time.strftime('%d %b %H:%M')}"
        button_text = button_team_text + button_time_text
        callback_data = f"match_id={match.id}"
        callback_button = types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
        markup.add(callback_button)
    return markup


def make_user_bets_keyboard(clients):
    markup = types.InlineKeyboardMarkup()
    for client in clients:
        telegram_id = client[0]
        name = client[1]
        callback_data = f"telegram_id={telegram_id}"
        callback_button = types.InlineKeyboardButton(text=name, callback_data=callback_data)
        markup.add(callback_button)
    return markup


def make_sample_keyboard():
    markup = types.InlineKeyboardMarkup()
    return markup


def make_sub_matches_keyboard(telegram_id: int):
    markup = types.ReplyKeyboardMarkup()
    button_make_bet = types.InlineKeyboardButton(text=menu_names.make_bet)
    button_show_bets = types.InlineKeyboardButton(text=menu_names.show_match_bets)
    button_to_menu = types.InlineKeyboardButton(text=menu_names.back_to_menu)
    markup.add(button_make_bet)
    markup.add(button_show_bets)
    markup.add(button_to_menu)

    if telegram_id in admin_lists:
        button_refresh_score = types.InlineKeyboardButton(text=menu_names.refresh_score)
        button_refresh_rates = types.InlineKeyboardButton(text=menu_names.refresh_rates)
        button_refresh_team_names = types.InlineKeyboardButton(text=menu_names.refresh_team_names)
        markup.add(button_refresh_score)
        markup.add(button_refresh_rates)
        markup.add(button_refresh_team_names)

    return markup
