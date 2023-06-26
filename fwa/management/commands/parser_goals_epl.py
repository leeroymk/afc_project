from pandas import read_html

from fwa.models import GoalscorersEPL
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Parse goals'

    def handle(self, *args, **options):

        def goals_parsing(goals_url):
            src = read_html(goals_url)
            goals_table = src[0]

            GoalscorersEPL.objects.all().delete()

            for index, row in goals_table.iterrows():
                model = GoalscorersEPL()
                model.position = row['№']
                model.player_name = row['Имя']
                model.team_name = row['Команда']
                model.goals = row['Голов'].split()[0]
                model.save()

        goals_url = 'http://fapl.ru/topscorers/'

        goals_parsing(goals_url)
