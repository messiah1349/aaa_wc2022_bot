import os
import sys
import yaml
from dataclasses import make_dataclass

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)


def read_config(config_path: str) -> dict:
    with open(config_path, 'r') as file:
        prime_service = yaml.safe_load(file)

    return prime_service


CONFIG_PATH = ROOT_DIR + '/configs/config.yaml'
config = read_config(CONFIG_PATH)


def get_menu_names():
    menu_naming = config['menu_naming']
    MenuNames = make_dataclass("MenuNames", [(eng, str, rus) for eng, rus in menu_naming.items()])
    menu_names = MenuNames()

    return menu_names


def get_admin_list():
    return config['admins_list']


def get_flag_emoji(code3: str) -> str:
    code3 = code3.upper()
    flags = config['flags']
    if code3 not in flags:
        return ''
    code2 = flags[code3]['code2']
    offset = ord('🇦') - ord('A')
    return chr(ord(code2[0]) + offset) + chr(ord(code2[1]) + offset)


def get_country_name(code3: str) -> str:
    code3 = code3.upper()
    flags = config['flags']
    if code3 not in flags:
        return code3
    country_name = flags[code3]['name']
    return country_name
