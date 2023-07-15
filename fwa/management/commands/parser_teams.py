import logging
import requests

from bs4 import BeautifulSoup
import lxml

from django.core.management.base import BaseCommand
from fwa.management.commands.utils import add_league, add_logo, add_name_url, add_slug, process_timer, headers


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse teams'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        logging_fwa.info('Наполнение БД с данными команд...')

        # Получаем список команд лиги и ссылки
        @process_timer
        def get_teams_data(league):
            logging_fwa.info(f'Наполняем БД клубами {league}')
            req = requests.get(league, headers=headers)
            soup = BeautifulSoup(req.text, 'lxml')
            teams_data = soup.find_all(class_='b-tag-table__content-team')
            league_name = soup.find('h1').text.split('-')[0].strip()

            for team in teams_data:
                team_name = team.find('a').text
                team_url = team.find('a')['href']
                # Добавляем имя, ссылку на страницу, лого и тэг в БД
                add_name_url(team_url, team_name)
                add_logo(team_url, team_name)
                add_slug(team_url, team_name)
                add_league(league_name, team_name)

        # Наполняем данные по командам АПЛ
        leagues_list = ['https://m.sports.ru/la-liga/table/',
                        'https://m.sports.ru/ligue-1/table/',
                        'https://m.sports.ru/bundesliga/table/',
                        'https://m.sports.ru/seria-a/table/',
                        'https://m.sports.ru/championship/table/',
                        'https://m.sports.ru/rfpl/table/',
                        'https://m.sports.ru/eredivisie/table/',
                        'https://m.sports.ru/bundesliga-austria/table/',
                        'https://m.sports.ru/primeira-liga/table/',
                        'https://m.sports.ru/super-lig/table/',
                        'https://m.sports.ru/epl/table/']

        for league in leagues_list:
            get_teams_data(league)

        logging_fwa.info('Наполнение БД с данными команд завершено!')
