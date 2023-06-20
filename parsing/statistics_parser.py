import sys
import logging
from random import choice
import time

import requests
from bs4 import BeautifulSoup
import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
import pandas as pd


logging.basicConfig(level=logging.INFO,
                    filename='log_parsing.log',
                    format="[%(asctime)s] %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
                    datefmt='%H:%M:%S',
                    )

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


def table_parser(table_url):
    req = requests.get(table_url, headers=random_headers())
    soup = BeautifulSoup(req.text, 'lxml')
    tournament_table = soup.find('table', class_='g-table-b')
    headers = [header.text for header in tournament_table.find_all('th')]
    tournament_data = []
    for team_data in tournament_table.find_all('tr'):
        row = [table_data.text for table_data in team_data.find_all('td')]
        print(row)
        tournament_data.append(row)
    try:
        table_result = pd.DataFrame(tournament_data[1:], columns=headers)
    except ValueError:
        table_result = None
        logging.error(f'Empty table at {table_url}')
    finally:
        logging.info(f'\n{table_result}')
        return table_result


def stats_parser(stats_page):
    soup = BeautifulSoup(stats_page, 'lxml')
    stats_data = soup.find('table', class_='b-tag-tournament-stat__table g-table-b')
    headers = [header.text for header in stats_data.find_all('th')]
    tournament_data = []
    for row_data in stats_data.find_all('tr'):
        row = [', '.join(row_element.text.strip().split('\n')) for row_element in row_data.find_all('td')]
        tournament_data.append(row)
    try:
        metric_result = pd.DataFrame(tournament_data[1:], columns=headers)
    except ValueError:
        metric_result = None
        logging.error('Empty stats list')
    finally:
        logging.info(f'\n{metric_result}')
        return metric_result


def selenium_clicker(stats_url, metric):
    try:
        browser.get(stats_url)
    except TimeoutException as te:
        logging.error(f'Ошибка {te} при парсинге таблицы "{metric}", пробуем второй раз')
        browser.close()
        browser.get(stats_url)
    finally:
        # Выбираем сезон
        select_season = WebDriverWait(browser, 10).until(
            expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'b-tag-tournament-stat__season-picker')))
        select = Select(select_season)
        select.select_by_visible_text("2022/2023")
        time.sleep(2)

        # Выбираем метрику
        select_metric = WebDriverWait(browser, 10).until(
            expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'b-tag-tournament-stat__type-picker')))
        select = Select(select_metric)
        select.select_by_value('goal_passes')
        select.select_by_value(metric)
        time.sleep(2)

        return browser.page_source


if __name__ == '__main__':

    def random_headers():
        return {'Accept': '*/*',
                'User-Agent': choice(desktop_agents),
                }

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
        )

    desktop_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPod; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; LM-Q710(FGN)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
        ]
    stats_url = 'https://m.sports.ru/epl/stat'
    table_url = 'https://m.sports.ru/epl/table/'

    # Парсим таблицу текущего сезона
    table_parser(table_url)

    # Выбираем метрику, запускаем ее парсинг
    chosen_metric = ['bombardiers', 'goal_passes']

    for metric in chosen_metric:
        stats_parser(selenium_clicker(stats_url, metric))

    browser.quit()
