import logging
import requests
from datetime import datetime

from bs4 import BeautifulSoup
import lxml
from pandas import read_html
from fwa.management.commands.req_fun import process_timer

from fwa.models import CalendarMatches, Teams
from django.core.management.base import BaseCommand
from django.db import connection, transaction


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse calendar'

    def handle(self, *args, **options):

        @process_timer
        def calendar_parsing(calendar_url):

            logging_fwa.info('Парсинг календаря ближайших встреч...')
            # Находим годы проведения сезона
            req = requests.get(calendar_url)
            soup = BeautifulSoup(req.text, 'lxml')
            season = soup.find('a', attrs={'selected': 'selected'}).text.strip()

            # Парсим календарь
            src = read_html(calendar_url, encoding='utf-8')
            calendar_table = src[1].drop(['Unnamed: 5', 'Зрители'], axis=1)

            with transaction.atomic():
                cursor = connection.cursor()
                cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(CalendarMatches._meta.db_table))

                for index, row in calendar_table.iterrows():
                    CalendarMatches.objects.create(
                        date_match=datetime.strptime(row['Дата'], '%d.%m.%Y|%H:%M'),
                        tournament=row['Турнир'],
                        opposite_team=Teams.objects.get(name=row['Соперник']),
                        place_match=row['Unnamed: 3'],
                        match_score=row['Счет'],
                        season=season
                        )

        calendar_url = 'https://www.sports.ru/arsenal/calendar/'
        calendar_parsing(calendar_url)
        logging_fwa.info('Парсинг календаря ближайших встреч завершен!')
