import logging
import requests

from bs4 import BeautifulSoup
import lxml
from pandas import read_html

from fwa.models import GoalscorersEPL, Teams
from fwa.management.commands.utils import headers, process_timer
from django.core.management.base import BaseCommand
from django.db import connection, transaction


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse goals'

    def handle(self, *args, **options):

        @process_timer
        @transaction.atomic
        def goals_parsing(goals_url):

            logging_fwa.info('Парсинг статистики бомбардиров...')

            # Находим годы проведения сезона
            req = requests.get(goals_url, headers=headers)
            soup = BeautifulSoup(req.text, 'lxml')
            selected = soup.find('h3').text.split()[-1].strip().split('/')[0]
            season = f'{selected}/{int(selected)+1}'

            # Парсим таблицу бомбардиров
            src = read_html(goals_url)
            goals_table = src[0]

            # Очищаем таблицу, рестарт присвоения ID
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(GoalscorersEPL._meta.db_table))

            for index, row in goals_table.iterrows():
                team = Teams.objects.get(name=row['Команда'])

                GoalscorersEPL.objects.create(
                    position=row['№'],
                    player=row['Имя'],
                    team=team,
                    goals=row['Голов'].split()[0],
                    season=season)

        # Демонстрационная таблица (сезон 2022/2023 завершился)
        goals_url = 'http://fapl.ru/topscorers/?season=17'

        # Актуальная таблица для парсинга
        # goals_url = 'http://fapl.ru/topscorers/'

        goals_parsing(goals_url)
        logging_fwa.info('Парсинг статистики бомбардиров завершен!')
