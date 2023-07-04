from pandas import read_html
from bs4 import BeautifulSoup
import logging
import requests

from fwa.models import StatEpl, Teams
from django.core.management.base import BaseCommand
from django.db import connection, transaction


root = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse table'

    def handle(self, *args, **options):

        root.info('EPL table is parsing...')

        def epl_table_parsing(table_url, season):
            src = read_html(table_url, encoding='utf-8')
            table_data = src[1]

            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}"'.format(StatEpl._meta.db_table))

            with transaction.atomic():
                for index, row in table_data.iterrows():
                    team, created = Teams.objects.get_or_create(name=row['Команда'])
                    if created:
                        logging.info(f"New team {row['Команда']} is added to the Teams table.")

                    model = StatEpl()
                    model.position = row['Unnamed: 0']
                    model.team = team
                    model.matches = row['М']
                    model.win = row['В']
                    model.draw = row['Н']
                    model.loss = row['П']
                    model.scored = row['Заб']
                    model.conceded = row['Проп']
                    model.points = row['О']
                    model.season = season
                    model.save()

        def year_parser(table_url):
            req = requests.get(table_url)
            soup = BeautifulSoup(req.text, 'html.parser')
            selected = soup.find_all('a', attrs={'selected': 'selected'})
            season = selected[1].text
            return season

        # table_url = 'https://www.sports.ru/epl/table/'
        table_url = 'https://www.sports.ru/epl/table/?s=270059&sub=table'
        season = year_parser(table_url)
        epl_table_parsing(table_url, season)
        root.info('OK!')
