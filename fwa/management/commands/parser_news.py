from collections import defaultdict
import logging
from urllib.parse import urlparse
import requests
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
import lxml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from django.core.management.base import BaseCommand

from fwa.models import News, Teams


logging_fwa = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse news'

    def add_arguments(self, parser):
        parser.add_argument('pages_qty', action='store', nargs='?', default=10, type=int)
        parser.add_argument('timeout_timer', action='store', nargs='?', default=60, type=int)

    def handle(self, *args, **options):

        logging_fwa.info('Парсинг новостей стартовал...')

        pages_qty = options['pages_qty']
        timeout_timer = options['timeout_timer']

        start_news_parsing = datetime.now()

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
        browser.set_page_load_timeout(timeout_timer)

        logging_fwa.info('Парсинг данных следующего соперника')

        # Парсинг новостей следующего соперника
        def rival_name_url(calendar_url):
            years = calendar_url.split('/')[-2]
            logging_fwa.info(f'Парсим ссылку и имя следующего соперника. Сезон {years}')
            req = requests.get(calendar_url)
            soup = BeautifulSoup(req.text, 'lxml')
            rows = soup.find('table', class_='stat-table').find_all('tr')
            if rows is not None:
                for row in rows:
                    links = row.find_all('a')
                    hrefs = [url['href'] for url in links]
                    names = [string.text for string in links]
                    if hrefs or names:
                        score_or_preview = names[3].strip()
                        if score_or_preview == 'превью':
                            team_url = hrefs[2].replace('/www.', '/m.')
                            team_name = names[2]
                            logging_fwa.info(f'Следующий соперник - {team_name}')
                            # Добавляем в БД логотип и тэг следующего соперника
                            add_logo(team_name, team_url)
                            add_tag(team_name, team_url)
                            return team_url, team_name
            else:
                return logging_fwa.warning('Следующий соперник не определен!')

        def next_rival_data(calendar_url):
            # Парсим новости следующего соперника
            rival = rival_name_url(calendar_url)
            if rival:
                for number in range(3):
                    try:
                        logging_fwa.info(f'Попытка парсинга данных следующего соперника {number + 1} из 3')
                        selenium_scroller(rival[0], rival[1])
                        break
                    except TimeoutException as te:
                        logging_fwa.error(f'Поймали {te}, пробуем еще раз')
                        continue
            return logging_fwa.warning('Новостей по следующему сопернику нет!')

        def add_logo(team_name, team_url):
            # Парсим ссылку на логотип
            logging_fwa.info(f'Парсим логотип команды {team_name}')
            req = requests.get(team_url)
            soup = BeautifulSoup(req.text, 'lxml')
            logo_soup = soup.find(class_='b-tag-header__tag-image')
            logo = logo_soup.img['data-src']

            if not Teams.objects.get(name=team_name).logo:
                logging_fwa.info(f'Добавляем ссылку на логотип {team_name}')
                logo_db = Teams(
                    name=team_name,
                    url=team_url,
                    logo=logo,
                )
                logo_db.save()
            return logging_fwa.info(f'Ссылка на логотип {team_name} уже существует в БД')

        def add_tag(team_name, team_url):
            # Добавляем тэг
            logging_fwa.info(f'Парсим тэг команды {team_name}')
            tag_team = team_url.replace('https://m.sports.ru', '').strip('/')
            if not Teams.objects.get(name=team_name).tag:
                logging_fwa.info(f'Добавляем тэг {team_name}')
                tag_db = Teams(
                    name=team_name,
                    url=team_url,
                    tag=tag_team,
                )
                tag_db.save()
            return logging_fwa.info(f'Тэг {team_name} уже существует в БД')

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

        # Получаем список команд лиги и ссылки
        def get_teams_urls(teams_table_site):
            logging_fwa.info('Получаем список команд лиги и ссылки')
            req = requests.get(teams_table_site)
            soup = BeautifulSoup(req.text, 'lxml')
            teams_list = soup.find_all(class_='b-tag-table__content-team')
            # Добавляем ссылки к ключам-названиям команды
            teams_urls = defaultdict()
            for team in teams_list:
                team_name = team.find('a').text
                team_url = team.find('a')['href']
                teams_urls[team_name] = team_url
            return teams_urls

        # Скроллим страницу
        def selenium_scroller(team_url, team_name):
            logging_fwa.info(f'Прокручиваем страницу {team_url}')
            if team_url and team_name:
                try:
                    browser.get(team_url)
                    # Здесь настраиваем количество страниц прокрутки
                    for i in range(pages_qty):
                        logging_fwa.info(f'Клик номер {i+1}')
                        btn_xpath = '//button[(contains(@class,"b-tag-lenta__show-more-button")) and(contains(text(),"Показать еще"))]'
                        more_btn = browser.find_element(By.XPATH, btn_xpath)
                        browser.execute_script("arguments[0].click();", more_btn)
                except (requests.RequestException, ValueError) as er:
                    browser.delete_all_cookies()
                    logging_fwa.error(f'Ошибка {er} при парсинге {team_url}')
                finally:
                    # Передаем в парсер новостей прокрученную страницу
                    get_team_news(browser.page_source, team_name)

        # Процесс парсинга новостей
        def get_team_news(scrolled_page, team_name):
            logging_fwa.info(f'Парсим новости команды {team_name}')
            soup = BeautifulSoup(scrolled_page, 'lxml')
            blog_news = soup.find_all(class_='b-tag-lenta__item m-type_blog')
            blog_counter = 0
            for bnew in blog_news:
                time_news = ''.join(bnew.find(class_='b-tag-lenta__item-details').text).strip()
                title = bnew.find('h2').text
                url = bnew.find('a')['href'].replace('//m.', '//')
                url_parsed = urlparse(url)
                url_res = f'{url_parsed.scheme}://{url_parsed.netloc}{url_parsed.path}'
                if title is None:
                    logging_fwa.warning(f'Заголовок пустой. Url: {url}\n')
                    continue
                team, created = Teams.objects.get_or_create(name=team_name)
                if created:
                    logging_fwa.info(f'Новая команда {team_name} добавлена в таблицу Teams.')
                if not News.objects.filter(source=url_res):
                    bnew_db = News(
                        date=timetyper(time_news),
                        team=team,
                        title=title,
                        source=url_res,
                        )
                    bnew_db.save()
                    blog_counter += 1
            logging_fwa.info(f'{blog_counter} блоговых новостей добавлены для команды {team_name}')
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
                    url = element.find('a')['href'].replace('//m.', '//')
                    url_parsed = urlparse(url)
                    url_res = f'{url_parsed.scheme}://{url_parsed.netloc}{url_parsed.path}'
                    if title is None:
                        logging_fwa.warning(f'Заголовок пустой. Url: {url}\n')
                        continue
                    team, created = Teams.objects.get_or_create(name=team_name)
                    if created:
                        logging_fwa.info(f'Новая команда {team_name} добавлена в таблицу Teams.')
                    if not News.objects.filter(source=url_res):
                        snew_db = News(
                            date=timetyper(news_exact_time),
                            team=team,
                            title=title,
                            source=url_res)
                        snew_db.save()
                        short_counter += 1
            logging_fwa.info(f'{short_counter} коротких новостей добавлены для команды {team_name}')

        # Парсим данные по следующему сопернику
        calendar_url = 'https://www.sports.ru/arsenal/calendar/2023-2024/'
        next_rival_data(calendar_url)

        # Наполняем данные по командам АПЛ
        teams_table_page = 'https://m.sports.ru/epl/table/'
        teams_urls = get_teams_urls(teams_table_page)

        # Парсим новости АПЛ
        team_counter = 0
        if teams_urls:
            logging_fwa.info(f'Парсер ищет на {pages_qty} страницах')
            logging_fwa.info(f'Таймер ожидания установлен на {timeout_timer} секунд')
            for team_name, team_url in teams_urls.items():
                team_counter += 1
                logging_fwa.info(f'{team_name} - это {team_counter} из {len(teams_urls)} команд')
                for number in range(5):
                    try:
                        logging_fwa.info(f'Попытка парсинга новостей {number + 1} из 5')
                        selenium_scroller(team_url, team_name)
                        break
                    except TimeoutException as te:
                        logging_fwa.error(f'Поймали {te}, пробуем еще раз')
                        continue
        else:
            logging_fwa.error('Что-то пошло не по плану...')

        browser.quit()

        finish_news_parsing = datetime.now()
        news_parse_time = finish_news_parsing-start_news_parsing
        res_time = news_parse_time.total_seconds()

        logging_fwa.info('Парсинг новостй успешно завершен!')
        logging_fwa.info(f'Время парсинга: {res_time} секунд!')
