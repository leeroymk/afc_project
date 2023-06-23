import logging
import sys
import requests
from random import choice
from datetime import datetime, timedelta

import lxml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError

from fwa.models import News, Teams
from . import parser_config


class Command(BaseCommand):
    help = 'Parse news'

    def add_arguments(self, parser):
        parser.add_argument('pages_qty', action='store', nargs='?', default=10)

    def handle(self, *args, **options):
        pages_qty = options['pages_qty']
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)

        logging.basicConfig(level=logging.INFO,
                            filename='log_parsing.log',
                            format="[%(asctime)s] %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
                            datefmt='%H:%M:%S',
                            )

        def timetyper(parsed):
            parsed = parsed.lower()
            if 'назад' in parsed:
                return datetime.now() - timedelta(minutes=int(parsed.split()[0]))
            elif 'сегодня' in parsed:
                d = datetime.now().day
                m = datetime.now().month
                y = datetime.now().year
            elif 'вчера' in parsed:
                d = (datetime.now() - timedelta(days=1)).day
                m = (datetime.now() - timedelta(days=1)).month
                y = (datetime.now() - timedelta(days=1)).year
            else:
                mdict = {
                    'янв': '01',
                    'фев': '02',
                    'мар': '03',
                    'апр': '04',
                    'май': '05',
                    'мая': '05',
                    'июн': '06',
                    'июл': '07',
                    'авг': '08',
                    'сен': '09',
                    'окт': '10',
                    'ноя': '11',
                    'дек': '12'
                }

                d = f'0{parsed.split()[0]}'[-2:]
                m = mdict[parsed.split()[1][:3]]
                y = datetime.now().year

            t = parsed.split()[-1]

            return datetime.strptime(' '.join(map(str, [d, m, y, t])), "%d %m %Y %H:%M")

        # Проверяем URL на возможность соединения
        def get_start_page_html(url):
            try:
                result = requests.get(url, headers=random_headers())
                result.raise_for_status()
                return result.text
            except (requests.RequestException, ValueError):
                logging.error('Сетевая ошибка')
                return False

        # Получаем список команд лиги и ссылки
        def get_teams_urls(html):
            teams_urls = {}
            soup = BeautifulSoup(html, 'lxml')
            teams_list = soup.find_all(class_='b-tag-table__content-team')
            # Добавляем ссылки к ключам-названиям команды
            for team in teams_list:
                teams_urls[team.find('a').text] = team.find('a')['href']
            return teams_urls

        # Скроллим страницу
        def selenium_scroller(team_url, team_name):
            browser.get(team_url)
            try:
                # Здесь настраиваем количество страниц прокрутки
                for i in range(pages_qty):
                    btn_xpath = '//button[(contains(@class,"b-tag-lenta__show-more-button")) and(contains(text(),"Показать еще"))]'
                    more_btn = browser.find_element(By.XPATH, btn_xpath)
                    browser.execute_script("arguments[0].click();", more_btn)
            except (requests.RequestException, ValueError) as er:
                logging.error(f'Ошибка {er} при парсинге {team_url}')
            finally:
                # Передаем в парсер новостей прокрученную страницу
                get_team_news(browser.page_source, team_name)

        # Процесс парсинга новостей
        def get_team_news(scrolled_page, team_name):
            soup = BeautifulSoup(scrolled_page, 'lxml')
            blog_news = soup.find_all(class_='b-tag-lenta__item m-type_blog')
            blog_counter = 0
            for bnew in blog_news:
                time_news = ''.join(
                    bnew.find(class_='b-tag-lenta__item-details').text).strip()
                title = bnew.find('h2').text
                url = bnew.find('a')['href']
                if title is None:
                    logging.info(f'Title is None. Url: {url}\n')
                    continue
                if not Teams.objects.filter(name=team_name):
                    t = Teams(name=team_name)
                    t.save()
                    logging.info(f'New team {team_name} is added to the Teams table.')
                if not News.objects.filter(source=url):
                    n = News(date=timetyper(time_news),
                             team=Teams.objects.filter(name=team_name).first(),
                             title=title,
                             source=url)
                    n.save()
                    blog_counter += 1
            logging.info(f'{blog_counter} blog news objects are added for {team_name}')
            short_news = soup.find_all(class_='b-tag-lenta__item m-type_news')
            short_counter = 0
            for snew in short_news:
                time_date = ''.join(
                    snew.find(class_='b-tag-lenta__item-details').text).strip()
                time_hours = snew.find_all(
                    class_='b-tag-lenta__item-news-item')
                for element in time_hours:
                    exact_time = element.find('time').text
                    news_exact_time = f'{time_date}, {exact_time}'
                    title = element.find('h2').text
                    url = element.find('a')['href']
                    if title is None:
                        logging.info(f'Title is None. Url: {url}\n')
                        continue
                    if not Teams.objects.filter(name=team_name):
                        t = Teams(name=team_name)
                        t.save()
                        logging.info(f'New team {team_name} is added to the Teams table.')
                    if not News.objects.filter(source=url):
                        n = News(date=timetyper(news_exact_time),
                                 team=Teams.objects.filter(name=team_name).first(),
                                 title=title,
                                 source=url)
                        n.save()
                        short_counter += 1
            logging.info(f'{short_counter} short news objects are added for {team_name}')

        desktop_agents = parser_config.DESKTOP_AGENTS

        def random_headers():
            return {'Accept': '*/*',
                    'User-Agent': choice(desktop_agents),
                    }

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )

        teams_table = parser_config.TEAMS_TABLE_SITE
        html = get_start_page_html(teams_table)
        teams_urls = get_teams_urls(html)
        team_counter = 0
        if html:
            logging.info(f'Parser searches in {pages_qty} pages')
            for team_name, team_url in teams_urls.items():
                team_counter += 1
                logging.info(f'{team_name} is the {team_counter} of {len(teams_urls)} teams')
                for _ in range(5):
                    try:
                        logging.info(f'Try #{_ + 1} of 5')
                        selenium_scroller(team_url, team_name)
                        break
                    except TimeoutException:
                        continue
        else:
            logging.error('Что-то пошло не по плану...')

        browser.quit()
