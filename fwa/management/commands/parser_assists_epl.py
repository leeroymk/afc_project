from bs4 import BeautifulSoup
import lxml
import logging
from pandas import read_html
import requests

from fwa.models import AssistentsEPL, Teams
from django.core.management.base import BaseCommand
from django.db import connection, transaction


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse assists'

    def handle(self, *args, **options):
        def assists_parsing(assists_url):

            logging_fwa.info('Парсинг статистики голевых передач...')
            # Находим годы проведения сезона
            req = requests.get(assists_url)
            soup = BeautifulSoup(req.text, 'lxml')
            season = soup.find('a', attrs={'selected': 'selected'}).text.strip()

            # Парсим таблицу ассистентов
            src = read_html(assists_url, encoding='utf-8')
            assists_table = src[1].drop(['М', 'Г', 'Пен', 'Г+П'], axis=1)

            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(AssistentsEPL._meta.db_table))

            with transaction.atomic():
                for index, row in assists_table.iterrows():
                    team, created = Teams.objects.get_or_create(name=row['Команда'])
                    if created:
                        logging_fwa.info(f"Новая команда - {row['Команда']} добавлена в таблицу Teams.")

                    model = AssistentsEPL()
                    model.position = row['Unnamed: 0']
                    model.player = row['Имя']
                    model.team = team
                    model.assists = row['П']
                    model.season = season
                    model.save()

        # Ссылка на статистику сезона 22/23
        assists_url = 'https://www.sports.ru/epl/bombardiers/?&s=goal_passes&d=1&season=270059'
        assists_parsing(assists_url)
        logging_fwa.info('Парсинг статистики голевых передач завершен!')
