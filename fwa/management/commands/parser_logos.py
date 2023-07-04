from collections import defaultdict
import requests

from bs4 import BeautifulSoup
import lxml

from django.core.management.base import BaseCommand
from fwa.models import Teams


class Command(BaseCommand):
    help = 'Parse news'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Чуть модифицированная функция get_teams_urls с использованием defaultdict
        table_url = 'https://m.sports.ru/epl/table/'
        teams_urls = defaultdict()
        table_page = requests.get(table_url)
        soup = BeautifulSoup(table_page.text, 'lxml')
        teams_list = soup.find_all(class_='b-tag-table__content-team')
        for team in teams_list:
            team_name = team.find('a').text
            team_url = team.find('a')['href']
            teams_urls[team_name] = {
                'url': team_url,
                }

        # Добавляем новый контент
        for name, data in teams_urls.items():
            # Добавляем тэг
            tag_team = data['url'].replace('https://m.sports.ru', '').strip('/')
            teams_urls[name]['tag'] = tag_team

            # Добавляем ссылку на логотип
            req = requests.get(data['url'])
            soup = BeautifulSoup(req.text, 'lxml')
            logo_soup = soup.find(class_='b-tag-header__tag-image')
            logo = logo_soup.img['data-src']
            teams_urls[name]['logo'] = logo

            t = Teams(
                name=name,
                url=data['url'],
                tag=tag_team,
                logo=logo,
            )
            t.save()
