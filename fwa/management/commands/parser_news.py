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
from django.core.management.base import BaseCommand

from fwa.models import News
from . import parser_config


class Command(BaseCommand):
    help = 'Parse news'

    def handle(self, *args, **options):
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
        def get_teams_urls(teams_list_epl):
            teams_urls = {}
            soup = BeautifulSoup(teams_list_epl, 'lxml')
            teams_list = soup.find_all(class_='b-tag-table__content-team')
            # Добавляем ссылки к ключам-названиям команды
            for team in teams_list:
                team_name = team.find('a').text
                team_url = team.find('a')['href']
                teams_urls.setdefault(team_name, team_url)
            return teams_urls

        # Скроллим страницу
        def selenium_scroller(team_url, team_name):
            try:
                browser.get(team_url)
                # Здесь настраиваем количество страниц прокрутки
                for i in range(parser_config.NUMBER_OF_PAGES):
                    btn_xpath = '//button[(contains(@class,"b-tag-lenta__show-more-button")) and(contains(text(),"Показать еще"))]'
                    more_btn = browser.find_element(By.XPATH, btn_xpath)
                    browser.execute_script("arguments[0].click();", more_btn)
            except (requests.RequestException, ValueError) as er:
                browser.delete_all_cookies()
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
                if not News.objects.filter(source=url):
                    n = News(date=timetyper(time_news),
                             team=team_name,
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
                    if not News.objects.filter(source=url):
                        n = News(date=timetyper(news_exact_time),
                                 team=team_name,
                                 title=title,
                                 source=url)
                        n.save()
                        short_counter += 1
            logging.info(f'{short_counter} short news objects are added for {team_name}')

        # Проверка на вхождение соперника в АПЛ
        # парсинг новостей команд-еврокубков
        def rival_name_url(calendar_url):
            req = requests.get(calendar_url)
            soup = BeautifulSoup(req.text, 'lxml')
            rows = soup.find('table', class_='stat-table').find_all('tr')
            for row in rows:
                links = row.find_all('a')
                hrefs = [url['href'] for url in links]
                names = [string.text for string in links]
                if hrefs or names:
                    score_or_preview = names[3].strip()
                    if score_or_preview == 'превью':
                        # competition = names[1]
                        href_team = hrefs[2].replace('/www.', '/m.')
                        team_name = names[2]
                        return href_team, team_name

        def random_headers():
            return {'Accept': '*/*',
                    'User-Agent': choice(parser_config.DESKTOP_AGENTS)}

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
        browser.set_page_load_timeout(30)

        calendar_url = 'https://www.sports.ru/arsenal/calendar/2023-2024/'
        teams_table_site = 'https://m.sports.ru/epl/table/'

        teams_list_epl = get_start_page_html(teams_table_site)
        teams_urls = get_teams_urls(teams_list_epl)

        # Парсим отдельно новости следующей команды (кубки)
        for number in range(3):
            try:
                logging.info(f'Try #{number + 1} out of 3')
                selenium_scroller(*rival_name_url(calendar_url))
                break
            except TypeError:
                logging.info('Enjoy your vacation!')
            except TimeoutException:
                continue

        # Парсим новости лиги
        team_counter = 0
        if teams_list_epl:
            logging.info(f'Parser searches in {parser_config.NUMBER_OF_PAGES} pages')
            for team_name, team_url in teams_urls.items():
                team_counter += 1
                logging.info(f'{team_name} is the {team_counter} of {len(teams_urls)} teams')
                for number in range(5):
                    try:
                        logging.info(f'Try #{number + 1} out of 5')
                        selenium_scroller(team_url, team_name)
                        break
                    except TimeoutException:
                        continue
        else:
            logging.error('Что-то пошло не по плану...')

        browser.quit()