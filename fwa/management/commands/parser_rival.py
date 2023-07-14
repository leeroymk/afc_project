import logging
import requests

from bs4 import BeautifulSoup
import lxml
from selenium.common.exceptions import TimeoutException

from django.core.management.base import BaseCommand
from fwa.management.commands.utils import add_logo, add_slug, add_name_url, process_timer, selenium_scroller, headers


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Next rival news'

    def add_arguments(self, parser):
        parser.add_argument('pages_qty', action='store', nargs='?', default=5, type=int)
        parser.add_argument('timeout_timer', action='store', nargs='?', default=70, type=int)

    @process_timer
    def handle(self, *args, **options):

        logging_fwa.info('Парсинг следующего соперника стартовал...')

        pages_qty = options['pages_qty']
        timeout_timer = options['timeout_timer']

        def next_rival_data(calendar_url):
            exception_counter = 0
            rival = db_rival_data(calendar_url)
            # Парсим новости и наполняем ДБ по следующему сопернику
            team_url = rival[0]
            team_name = rival[1]
            for number in range(3):
                try:
                    logging_fwa.info(f'Парсер ищет на {pages_qty+1} страницах')
                    logging_fwa.info(f'Таймер ожидания установлен на {timeout_timer} секунд')
                    logging_fwa.info(f'Попытка парсинга новостей следующего соперника {number + 1} из 3')
                    selenium_scroller(team_url, team_name, pages_qty, timeout_timer)
                    break
                except TimeoutException as te:
                    logging_fwa.error(f'Поймали {te.msg}\nПробуем еще раз...')
                    continue
            logging_fwa.info('Парсинг новостей успешно завершен!')

        # Заносим в БД информацию о следующем сопернике
        def db_rival_data(calendar_url):
            years = calendar_url.split('/')[-2]
            logging_fwa.info(f'Парсим ссылку и имя следующего соперника. Сезон {years}')
            req = requests.get(calendar_url, headers=headers)
            soup = BeautifulSoup(req.text, 'lxml')
            rows = soup.find('table', class_='stat-table').find_all('tr')
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
                        add_slug(team_url, team_name)
                        return team_url, team_name
            logging_fwa.warning('Следующий соперник не определен!')

        # Парсим данные по следующему сопернику
        calendar_url = 'https://www.sports.ru/arsenal/calendar/2023-2024/'
        next_rival_data(calendar_url)

        logging_fwa.info('Парсинг данных следующего соперника успешно завершен!')
