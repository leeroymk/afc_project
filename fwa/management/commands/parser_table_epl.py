from pandas import read_html
from bs4 import BeautifulSoup
import lxml
import logging
import requests

from fwa.management.commands.req_fun import process_timer, headers
from fwa.models import StatEpl, Teams
from django.core.management.base import BaseCommand
from django.db import connection, transaction


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse table'

    def handle(self, *args, **options):

        logging_fwa.info('Парсинг таблицы АПЛ...')

        @process_timer
        @transaction.atomic
        def epl_table_parsing(table_url, season):
            # Парсим таблицу АПЛ
            src = read_html(table_url, encoding='utf-8')
            table_data = src[1]

            # Очищаем таблицу, рестарт присвоения ID
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(StatEpl._meta.db_table))

            for index, row in table_data.iterrows():
                team, created = Teams.objects.get_or_create(name=row['Команда'])
                if created:
                    logging.info(f"Новая команда {team.name} добавлена в БД.")

                StatEpl.objects.create(
                    position=row['Unnamed: 0'],
                    team=team,
                    matches=row['М'],
                    win=row['В'],
                    draw=row['Н'],
                    loss=row['П'],
                    scored=row['Заб'],
                    conceded=row['Проп'],
                    points=row['О'],
                    season=season
                )

        def year_parser(table_url):
            req = requests.get(table_url, headers=headers)
            soup = BeautifulSoup(req.text, 'lxml')
            selected = soup.find_all('a', attrs={'selected': 'selected'})
            season = selected[1].text
            return season

        # Демонстрационная таблица (сезон 2022/2023 завершился)
        table_url = 'https://www.sports.ru/epl/table/?s=270059&sub=table'

        # Актуальная таблица для парсинга
        # table_url = 'https://www.sports.ru/epl/table/'

        season = year_parser(table_url)
        epl_table_parsing(table_url, season)

        logging_fwa.info('Парсинг таблицы АПЛ завершен!')
