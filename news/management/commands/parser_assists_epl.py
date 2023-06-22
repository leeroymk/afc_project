import pandas as pd

from news.models import AssistentsEPL
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Parse assists'

    def handle(self, *args, **options):

        def assists_parsing(assists_url):
            src = pd.read_html(assists_url, encoding='utf-8')
            assists_table = src[1]
            assists_table.drop(['М', 'Г', 'Пен', 'Г+П'], axis=1)
            AssistentsEPL.objects.all().delete()

            for index, row in assists_table.iterrows():
                model = AssistentsEPL()
                model.position = row['Unnamed: 0']
                model.player_name = row['Имя']
                model.team_name = row['Команда']
                model.assists = row['П']
                model.save()

        # Ссылка на статистику сезона 22/23, нужно обновить в августе
        assists_url = 'https://www.sports.ru/epl/bombardiers/?&s=goal_passes&d=1&season=270059'

        assists_parsing(assists_url)
