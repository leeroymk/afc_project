import logging
import requests
from datetime import datetime

from bs4 import BeautifulSoup
from pandas import read_html

from fwa.models import CalendarMatches
from django.core.management.base import BaseCommand
from django.db import connection, transaction


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse calendar'

    def handle(self, *args, **options):
        def calendar_parsing(calendar_url):

            logging_fwa.info('Calendar is parsing...')
            # Находим годы проведения сезона
            req = requests.get(calendar_url)
            soup = BeautifulSoup(req.text, 'lxml')
            season = soup.find('a', attrs={'selected': 'selected'}).text.strip()

            # Парсим календарь
            src = read_html(calendar_url, encoding='utf-8')
            calendar_table = src[1].drop(['Unnamed: 5', 'Зрители'], axis=1)

            # Чистим данные таблицы
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}"'.format(CalendarMatches._meta.db_table))

            with transaction.atomic():
                for index, row in calendar_table.iterrows():
                    model = CalendarMatches()
                    model.date_match = datetime.strptime(row['Дата'], '%d.%m.%Y|%H:%M')
                    model.tournament = row['Турнир']
                    model.opposite_team = row['Соперник']
                    model.place_match = row['Unnamed: 3']
                    model.match_score = row['Счет']
                    model.season = season
                    model.save()

        calendar_url = 'https://www.sports.ru/arsenal/calendar/'
        calendar_parsing(calendar_url)
        logging_fwa.info('Calendar parsing DONE!')
