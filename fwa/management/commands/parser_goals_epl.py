from bs4 import BeautifulSoup
from pandas import read_html
import requests

from fwa.models import GoalscorersEPL
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Parse goals'

    def handle(self, *args, **options):

        def goals_parsing(goals_url):
            # Находим годы проведения сезона
            req = requests.get(goals_url)
            soup = BeautifulSoup(req.text, 'lxml')
            selected = soup.find('h3').text.split()[-1].strip().split('/')[0]
            season = f'{selected}/{int(selected)+1}'

            # Парсим таблицу бомбардиров
            src = read_html(goals_url)
            goals_table = src[0]

            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}"'.format(GoalscorersEPL._meta.db_table))

            for index, row in goals_table.iterrows():
                model = GoalscorersEPL()
                model.position = row['№']
                model.player_name = row['Имя']
                model.team_name = row['Команда']
                model.goals = row['Голов'].split()[0]
                model.season = season
                model.save()

        goals_url = 'http://fapl.ru/topscorers/'

        goals_parsing(goals_url)
