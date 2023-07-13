import logging
import requests
from datetime import datetime

from bs4 import BeautifulSoup
import lxml
from pandas import read_html

from fwa.management.commands.req_fun import process_timer, headers
from fwa.models import CalendarMatches, Teams
from django.core.management.base import BaseCommand
from django.db import connection, transaction


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse calendar'

    @process_timer
    def handle(self, *args, **options):

        # Очищаем таблицу, рестарт присвоения ID
        cursor = connection.cursor()
        cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(CalendarMatches._meta.db_table))

        @transaction.atomic
        def calendar_parsing(calendar_url, team_q):

            logging_fwa.info(f'Парсинг календаря ближайших встреч для {team_q.name}...')
            # Находим годы проведения сезона
            req = requests.get(calendar_url, headers=headers)
            soup = BeautifulSoup(req.text, 'lxml')
            season = soup.find('a', attrs={'selected': 'selected'}).text.strip()

            # Парсим календарь
            src = read_html(calendar_url, encoding='utf-8')
            calendar_table = src[1].drop(['Unnamed: 5', 'Зрители'], axis=1)

            for index, row in calendar_table.iterrows():
                rival, created = Teams.objects.get_or_create(name=row['Соперник'])
                if created:
                    logging.info(f"Новая команда {rival.name} добавлена в БД.")

                CalendarMatches.objects.create(
                    date_match=datetime.strptime(row['Дата'], '%d.%m.%Y|%H:%M'),
                    tournament=row['Турнир'],
                    place_match=row['Unnamed: 3'],
                    match_score=row['Счет'],
                    season=season,
                    team=team_q,
                    rival=rival)

        for team_q in Teams.objects.all():
            calendar_url = f'https://www.sports.ru/{team_q.slug}/calendar/'
            calendar_parsing(calendar_url, team_q)
            logging_fwa.info(f'Парсинг календаря ближайших встреч для команды {team_q.name} завершен!')
