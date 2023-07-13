from collections import defaultdict
import logging
import requests

from bs4 import BeautifulSoup
import lxml
from django.core.management.base import BaseCommand
from fwa.management.commands.req_fun import process_timer, selenium_scroller
from selenium.common.exceptions import TimeoutException


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse news'

    def add_arguments(self, parser):
        parser.add_argument('pages_qty', action='store', nargs='?', default=2, type=int)
        parser.add_argument('timeout_timer', action='store', nargs='?', default=40, type=int)

    @process_timer
    def handle(self, *args, **options):

        logging_fwa.info('Парсинг новостей стартовал...')

        pages_qty = options['pages_qty']
        timeout_timer = options['timeout_timer']

        # Получаем список команд лиги и ссылки
        def get_urls_teams_dict(teams_table_site):
            logging_fwa.info('Получаем список команд лиги и ссылки')
            req = requests.get(teams_table_site)
            soup = BeautifulSoup(req.text, 'lxml')
            teams_list = soup.find_all(class_='b-tag-table__content-team')
            # Добавляем ссылки к ключам-названиям команды
            teams_urls = defaultdict()
            for team in teams_list:
                team_name = team.find('a').text
                team_url = team.find('a')['href']
                teams_urls[team_url] = team_name
            return teams_urls

        # Наполняем данные по командам АПЛ
        teams_table_page = 'https://m.sports.ru/epl/table/'
        teams_urls = get_urls_teams_dict(teams_table_page)

        # Парсим новости АПЛ
        team_counter = 0
        if teams_urls:
            logging_fwa.info(f'Парсер ищет на {pages_qty} страницах')
            logging_fwa.info(f'Таймер ожидания установлен на {timeout_timer} секунд')
            for team_url, team_name in teams_urls.items():
                team_counter += 1
                logging_fwa.info(f'{team_name} - это {team_counter} из {len(teams_urls)} команд')
                for number in range(5):
                    try:
                        logging_fwa.info(f'Попытка парсинга новостей команды {team_name} {number + 1} из 5')
                        selenium_scroller(team_url, team_name, pages_qty, timeout_timer)
                        break
                    except TimeoutException as te:
                        logging_fwa.error(f'Поймали {te}\nПробуем еще раз...')
                        continue
                logging_fwa.info(f'Парсинг новостей команды {team_name} завершен!')
        else:
            logging_fwa.error('Что-то пошло не по плану...')

        logging_fwa.info('Парсинг новостй успешно завершен!')
