from datetime import datetime, timedelta
import logging
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from fwa.models import News, Teams


logging_fwa = logging.getLogger(__name__)


def add_name_url(team_url, team_name):
    # Добавляем в БД название команды
    logging_fwa.info(f'Парсим название и ссылку на страницу команды {team_name}')
    team_q, created = Teams.objects.get_or_create(name=team_name)
    if created:
        logging_fwa.info(f'Новая команда {team_q.name} добавлена в БД.')
    else:
        logging_fwa.debug(f'Команда {team_q.name} уже существует в БД.')
    # Дополняем БД ссылками на страницы клубов
    if Teams.objects.get(name=team_q.name) and not Teams.objects.get(name=team_q.name).url:
        logging_fwa.debug(f'Добавляем ссылку на логотип {team_q.name}')
        Teams(name=team_name, url=team_url).save()
        logging_fwa.info(f'Ссылка на страницу {team_q.name} добавлена в БД')
    else:
        logging_fwa.debug(f'Ссылка на страницу {team_q.name} уже существует в БД')


def add_logo(team_url, team_name):
    # Парсим ссылку на логотип
    logging_fwa.info(f'Парсим логотип команды {team_name}')
    req = requests.get(team_url)
    soup = BeautifulSoup(req.text, 'lxml')
    logo_soup = soup.find(class_='b-tag-header__tag-image')
    logo = logo_soup.img['data-src']
    if not Teams.objects.get(name=team_name).logo:
        logging_fwa.debug(f'Добавляем ссылку на логотип {team_name}')
        Teams(name=team_name, url=team_url, logo=logo,).save()
        logging_fwa.info(f'Ссылка на логотип {team_name} добавлена в БД')
    else:
        logging_fwa.debug(f'Ссылка на логотип {team_name} уже существует в БД')


def add_tag(team_url, team_name):
    # Добавляем тэг
    logging_fwa.info(f'Парсим тэг команды {team_name}')
    tag_team = team_url.replace('https://m.sports.ru', '').strip('/')
    if not Teams.objects.get(name=team_name).tag:
        logging_fwa.debug(f'Добавляем тэг {team_name}')
        Teams(name=team_name, url=team_url, tag=tag_team).save()
        logging_fwa.info(f'Тэг {team_name} добавлен в БД')
    else:
        logging_fwa.debug(f'Тэг {team_name} уже существует в БД')


def selenium_scroller(team_url, team_name):
    logging_fwa.info(f'Прокручиваем страницу {team_url}')
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                   options=chrome_options)
        browser.set_page_load_timeout(30)
        browser.get(team_url)

        for i in range(5):
            logging_fwa.info(f'Клик номер {i+1}')
            btn_xpath = '//button[(contains(@class,"b-tag-lenta__show-more-button")) and(contains(text(),"Показать еще"))]'
            more_btn = browser.find_element(By.XPATH, btn_xpath)
            browser.execute_script("arguments[0].click();", more_btn)
    except TimeoutException as er:
        browser.delete_all_cookies()
        logging_fwa.error(f'Ошибка {er} при парсинге {team_url}!\nПробуем еще...')
    finally:
        # Передаем в парсер новостей прокрученную страницу
        get_team_news(browser.page_source, team_name)
        browser.quit()


# Процесс парсинга новостей
def get_team_news(scrolled_page, team_name):
    logging_fwa.info(f'Парсим новости команды {team_name}...')
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
        team = Teams.objects.get(name=team_name)
        if not News.objects.filter(source=url_res):
            News(date=timetyper(time_news), team=team, title=title, source=url_res).save()
            blog_counter += 1
    logging_fwa.info(f'{blog_counter} блоговых новостей добавлены для команды {team_name}')
    short_news = soup.find_all(class_='b-tag-lenta__item m-type_news')
    short_counter = 0
    for snew in short_news:
        time_date = ''.join(snew.find(class_='b-tag-lenta__item-details').text).strip()
        time_hours = snew.find_all(class_='b-tag-lenta__item-news-item')
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
            team = Teams.objects.get(name=team_name)
            if not News.objects.filter(source=url_res):
                News(date=timetyper(news_exact_time), team=team, title=title, source=url_res).save()
                short_counter += 1
    logging_fwa.info(f'{short_counter} коротких новостей добавлены для команды {team_name}')


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


def process_timer(fun):
    def wrapper(*args, **kwargs):
        start = time.time()
        fun(*args, **kwargs)
        finish = time.time()
        res_time = round((finish - start), 1)
        logging_fwa.info(f'Время парсинга составило {res_time} секунд!')
    return wrapper
