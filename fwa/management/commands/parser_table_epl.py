from pandas import read_html
from bs4 import BeautifulSoup
import requests

from fwa.models import StatEpl
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Parse table'

    def handle(self, *args, **options):

        def epl_table_parsing(table_url, season):
            src = read_html(table_url, encoding='utf-8')
            table_data = src[1]

            StatEpl.objects.all().delete()

            for index, row in table_data.iterrows():
                model = StatEpl()
                model.position = row['Unnamed: 0']
                model.team = row['Команда']
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

        table_url = 'https://www.sports.ru/epl/table/'
        season = year_parser(table_url)
        epl_table_parsing(table_url, season)
