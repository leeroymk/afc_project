import logging
import requests
from datetime import datetime

from bs4 import BeautifulSoup
import lxml
from selenium.common.exceptions import TimeoutException
from django.core.management.base import BaseCommand
from fwa.management.commands.req_fun import add_logo, add_tag, add_name_url, selenium_scroller


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Next rival news'

    def add_arguments(self, parser):
        parser.add_argument('pages_qty', action='store', nargs='?', default=10, type=int)
        parser.add_argument('timeout_timer', action='store', nargs='?', default=60, type=int)

    def handle(self, *args, **options):
        start = datetime.now()
        logging_fwa.info('Парсинг следующего соперника стартовал...')

        def next_rival_data(calendar_url):
            rival = db_rival_data(calendar_url)
            # Парсим новости и наполняем ДБ по следующему сопернику
            team_url = rival[0]
            team_name = rival[1]
            for number in range(3):
                try:
                    logging_fwa.info(f'Попытка парсинга новостей следующего соперника {number + 1} из 3')
                    selenium_scroller(team_url, team_name)
                    break
                except TimeoutException as te:
                    logging_fwa.error(f'Поймали {te}!\nПробуем еще раз...')
                    continue

        # Заносим в БД информацию о следующем сопернике
        def db_rival_data(calendar_url):
            years = calendar_url.split('/')[-2]
            logging_fwa.info(f'Парсим ссылку и имя следующего соперника. Сезон {years}')
            req = requests.get(calendar_url)
            soup = BeautifulSoup(req.text, 'lxml')
            rows = soup.find('table', class_='stat-table').find_all('tr')
            if rows:
                for row in rows:
                    links = row.find_all('a')
                    hrefs = [url['href'] for url in links]
                    names = [string.text for string in links]
                    if hrefs or names:
                        score_or_preview = names[3].strip()
                        if score_or_preview == 'превью':
                            team_url = hrefs[2].replace('/www.', '/m.')
                            team_name = names[2]
                            logging_fwa.info(f'Следующий соперник - {team_name}')
                            add_name_url(team_url, team_name)
                            add_logo(team_url, team_name)
                            add_tag(team_url, team_name)
                            return team_url, team_name
            logging_fwa.warning('Следующий соперник не определен!')

        # Парсим данные по следующему сопернику
        calendar_url = 'https://www.sports.ru/arsenal/calendar/2023-2024/'
        next_rival_data(calendar_url)

        finish = datetime.now()
        rival_parse_time = finish-start
        res_time = rival_parse_time.total_seconds()
        logging_fwa.info(f'Время парсинга: {res_time} секунд!')

        logging_fwa.info('Парсинг данных следующего соперника успешно завершен!')
