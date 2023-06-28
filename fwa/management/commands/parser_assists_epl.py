from bs4 import BeautifulSoup
import pandas as pd
import requests

from fwa.models import AssistentsEPL
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Parse assists'

    def handle(self, *args, **options):
        def assists_parsing(assists_url):
            # Находим годы проведения сезона
            req = requests.get(assists_url)
            soup = BeautifulSoup(req.text, 'html.parser')
            season = soup.find('a', attrs={'selected': 'selected'}).text.strip()

            # Парсим таблицу ассистентов
            src = pd.read_html(assists_url, encoding='utf-8')
            assists_table = src[1].drop(['М', 'Г', 'Пен', 'Г+П'], axis=1)

            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}"'.format(AssistentsEPL._meta.db_table))

            for index, row in assists_table.iterrows():
                model = AssistentsEPL()
                model.position = row['Unnamed: 0']
                model.player_name = row['Имя']
                model.team_name = row['Команда']
                model.assists = row['П']
                model.season = season
                model.save()

        # Ссылка на статистику сезона 22/23
        assists_url = 'https://www.sports.ru/epl/bombardiers/?&s=goal_passes&d=1&season=270059'
        assists_parsing(assists_url)
