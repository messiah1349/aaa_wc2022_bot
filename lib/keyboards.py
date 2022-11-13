import os
import sys
from telebot import types

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)

import lib.utils as ut
menu_names = ut.get_menu_names()


def make_not_registered_welcome_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(menu_names.user_registration)
    return markup


def make_welcome_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    # markup.add(menu_names.user_registration)
    markup.add(menu_names.show_matches)
    markup.add(menu_names.add_match)
    markup.add(menu_names.show_leaderboard)
    markup.add(menu_names.show_user_bets)
    return markup


def make_matches_keyboard(matches):
    markup = types.InlineKeyboardMarkup()
    for match in matches:
        button_text = f"{match.home_team} - {match.away_team}"
        callback_data = f"match_id={match.id}"
        callback_button = types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
        markup.add(callback_button)
    return markup


def make_sub_matches_keyboard():
    markup = types.ReplyKeyboardMarkup()
    button_make_bet = types.InlineKeyboardButton(text=menu_names.make_bet)
    button_refresh_score = types.InlineKeyboardButton(text=menu_names.refresh_score)
    button_refresh_rates = types.InlineKeyboardButton(text=menu_names.refresh_rates)
    # button_show_match = types.InlineKeyboardButton(text=menu_names.show_match_info)
    button_show_bets = types.InlineKeyboardButton(text=menu_names.show_match_bets)
    markup.add(button_make_bet)
    markup.add(button_refresh_score)
    markup.add(button_refresh_rates)
    # markup.add(button_show_match)
    markup.add(button_show_bets)

    return markup


def make_bet_keyboard(match):

    markup = types.InlineKeyboardMarkup()
    home_text = f"{match.home_team} победит, кэф - {match.home_rate}"
    draw_text = f"Ничья, кэф - {match.draw_rate}"
    away_text = f"{match.away_team} победит, кэф - {match.away_rate}"
    home_button = types.InlineKeyboardButton(text=home_text, callback_data=f'outcome_bet_w1_{match.id}')
    draw_button = types.InlineKeyboardButton(text=draw_text, callback_data=f'outcome_bet_dd_{match.id}')
    away_button = types.InlineKeyboardButton(text=away_text, callback_data=f'outcome_bet_w2_{match.id}')
    markup.add(home_button)
    markup.add(draw_button)
    markup.add(away_button)

    return markup
