import logging

from pandas import read_html
import requests
from bs4 import BeautifulSoup
import lxml

from fwa.models import AssistantsEPL, Teams
from fwa.management.commands.utils import headers, process_timer
from django.core.management.base import BaseCommand
from django.db import connection, transaction

logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse assists'

    def handle(self, *args, **options):

        @process_timer
        @transaction.atomic
        def assists_parsing(assists_url):

            logging_fwa.info('Парсинг статистики голевых передач...')
            # Находим годы проведения сезона
            req = requests.get(assists_url, headers=headers)
            soup = BeautifulSoup(req.text, 'lxml')
            season = soup.find('a', attrs={'selected': 'selected'}).text.strip()

            # Парсим таблицу ассистентов
            src = read_html(assists_url, encoding='utf-8')
            assists_table = src[1].drop(['М', 'Г', 'Пен', 'Г+П'], axis=1)

            # Очищаем таблицу, рестарт присвоения ID
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(AssistantsEPL._meta.db_table))

            for index, row in assists_table.iterrows():
                team = Teams.objects.get(name=row['Команда'])
                AssistantsEPL.objects.create(
                    position=row['Unnamed: 0'],
                    player=row['Имя'],
                    assists=row['П'],
                    season=season,
                    team=team)

        # Демонстрационная таблица (сезон 2022/2023 завершился)
        assists_url = 'https://www.sports.ru/epl/bombardiers/?&s=goal_passes&d=1&season=270059'

        # Актуальная таблица для парсинга
        # assists_url = 'https://www.sports.ru/epl/bombardiers/'

        assists_parsing(assists_url)
        logging_fwa.info('Парсинг статистики голевых передач завершен!')
