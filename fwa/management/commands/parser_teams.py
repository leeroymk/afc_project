import logging
import requests

from bs4 import BeautifulSoup
import lxml
from django.core.management.base import BaseCommand
from fwa.management.commands.req_fun import add_logo, add_name_url, add_slug, process_timer


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse teams'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        logging_fwa.info('Наполнение БД с данными команд...')

        # Получаем список команд лиги и ссылки
        @process_timer
        def get_teams_data(teams_table_site):
            logging_fwa.info('Наполняем БД клубами АПЛ и ссылками на их страницы')
            req = requests.get(teams_table_site)
            soup = BeautifulSoup(req.text, 'lxml')
            teams_data = soup.find_all(class_='b-tag-table__content-team')

            for team in teams_data:
                team_name = team.find('a').text
                team_url = team.find('a')['href']
                # Добавляем имя, ссылку на страницу, лого и тэг в БД
                add_name_url(team_url, team_name)
                add_logo(team_url, team_name)
                add_slug(team_url, team_name)

        # Наполняем данные по командам АПЛ
        teams_table_page = 'https://m.sports.ru/epl/table/'
        get_teams_data(teams_table_page)

        logging_fwa.info('Наполнение БД с данными команд завершено!')
