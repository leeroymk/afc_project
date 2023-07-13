from datetime import datetime, timedelta
import logging
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from django.db import OperationalError

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from fwa.models import News, Teams


logging_fwa = logging.getLogger(__name__)


# Счетчик работы функции
def process_timer(fun):
    def wrapper(*args, **kwargs):
        start = time.time()
        fun(*args, **kwargs)
        finish = time.time()
        res_time = round((finish - start), 1)
        logging_fwa.info(f'Время работы функции {fun.__name__} составило {res_time} сек')
    return wrapper


# Обработчик времени
def timetyper(parsed_time):
    parsed_time = parsed_time.lower()
    if 'назад' in parsed_time:
        actual_date = datetime.now() - timedelta(minutes=int(parsed_time.split()[0]))
        d, m, y = actual_date.day, actual_date.month, actual_date.year
        t = datetime.strftime(actual_date, "%H:%M")
    elif 'сегодня' in parsed_time:
        actual_date = datetime.now()
        d, m, y = actual_date.day, actual_date.month, actual_date.year
        t = parsed_time.split()[-1]
    elif 'вчера' in parsed_time:
        actual_date = datetime.now() - timedelta(days=1)
        d, m, y = actual_date.day, actual_date.month, actual_date.year
        t = parsed_time.split()[-1]
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

        d = f'0{parsed_time.split()[0]}'[-2:]
        m = mdict[parsed_time.split()[1][:3]]
        if len(parsed_time.split()) == 3:
            y = datetime.now().year
        else:
            y = parsed_time.split()[2][:4]
        t = parsed_time.split()[-1]
    return datetime.strptime(' '.join(map(str, [d, m, y, t])), "%d %m %Y %H:%M")


# Добавляем имя и ссылку на страницу в БД
def add_name_url(team_url, team_name):
    # Добавляем в БД название команды
    if not Teams.objects.filter(name=team_name):
        logging_fwa.info(f'Парсим название и ссылку на страницу команды {team_name}')
        team_q, created = Teams.objects.get_or_create(name=team_name)
        if created:
            logging_fwa.info(f'Новая команда {team_q.name} добавлена в БД.')
        else:
            logging_fwa.info(f'Команда {team_q.name} уже существует в БД.')
    # Дополняем БД ссылками на страницы клубов
    if not Teams.objects.get(name=team_name).url:
        logging_fwa.info(f'Добавляем ссылку на логотип {team_name}')
        Teams.objects.filter(name=team_name).update(url=team_url)
        logging_fwa.info(f'Ссылка на страницу {team_name} добавлена в БД')
    else:
        logging_fwa.info(f'Ссылка на страницу {team_name} уже существует в БД')


# Добавляем лого в БД
def add_logo(team_url, team_name):
    # Парсим ссылку на логотип
    if not Teams.objects.get(name=team_name).logo:
        logging_fwa.info(f'Парсим ссылку на логотип {team_name}')
        req = requests.get(team_url)
        soup = BeautifulSoup(req.text, 'lxml')
        logo_soup = soup.find(class_='b-tag-header__tag-image')
        logo_url = logo_soup.img['data-src']
        Teams.objects.filter(name=team_name).update(logo=logo_url)
        logging_fwa.info(f'Ссылка на логотип {team_name} добавлена в БД')
    else:
        logging_fwa.info(f'Ссылка на логотип {team_name} уже существует в БД')


# Добавляем тэг в БД
def add_tag(team_url, team_name):
    if not Teams.objects.get(name=team_name).tag:
        # Добавляем тэг
        logging_fwa.info(f'Парсим тэг команды {team_name}')
        tag_team = team_url.replace('https://m.sports.ru', '').strip('/')
        Teams.objects.filter(name=team_name).update(tag=tag_team)
        logging_fwa.info(f'Тэг {team_name} добавлен в БД')
    else:
        logging_fwa.info(f'Тэг {team_name} уже существует в БД')


# Прокрутчик страницы
@process_timer
def selenium_scroller(team_url, team_name, pages_qty, timeout_timer):
    logging_fwa.info(f'Прокручиваем страницу {team_url}')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options)
    browser.set_page_load_timeout(timeout_timer)
    wait = WebDriverWait(browser, 10)
    browser.get(team_url)
    for i in range(pages_qty):
        btn_xpath = '//button[(contains(@class,"b-tag-lenta__show-more-button")) and(contains(text(),"Показать еще"))]'
        wait.until(lambda browser: browser.execute_script('return document.readyState') == 'complete')
        logging_fwa.info(f'Клик номер {i+1}')
        more_btn = browser.find_element(By.XPATH, btn_xpath)
        browser.execute_script("arguments[0].click();", more_btn)
    # Передаем в парсер новостей прокрученную страницу
    logging_fwa.info('Страницу прокрутили успешно, передаем в парсер новостей...')
    get_team_news(browser.page_source, team_name)
    browser.quit()


# Процесс парсинга новостей
@process_timer
def get_team_news(scrolled_page, team_name):
    try:
        logging_fwa.info(f'Парсим новости команды {team_name}...')
        soup = BeautifulSoup(scrolled_page, 'lxml')
        blog_news = soup.find_all(class_='b-tag-lenta__item m-type_blog')
        blog_counter = 0
        for bnew in blog_news:
            time_news = timetyper(bnew.find(class_='b-tag-lenta__item-details').text)
            title = bnew.find('h2').text
            url = bnew.find('a')['href'].replace('//m.', '//')
            url_parsed = urlparse(url)
            url_res = f'{url_parsed.scheme}://{url_parsed.netloc}{url_parsed.path}'
            if title is None:
                logging_fwa.warning(f'Заголовок пустой. Url: {url}\n')
                continue
            team_q = Teams.objects.get(name=team_name)
            if not News.objects.filter(source=url_res).exists():
                News.objects.create(
                    date=time_news,
                    team=team_q,
                    title=title,
                    source=url_res)
                blog_counter += 1
                logging_fwa.info(f'Добавленая блоговая новость {url_res}')
        logging_fwa.info(f'{blog_counter} блоговых новостей добавлены для команды {team_name}')
        short_news = soup.find_all(class_='b-tag-lenta__item m-type_news')
        short_counter = 0
        for snew in short_news:
            time_date = snew.find(class_='b-tag-lenta__item-details').text.strip()
            time_hours = snew.find_all(class_='b-tag-lenta__item-news-item')
            for element in time_hours:
                exact_time = element.find('time').text
                news_exact_time = timetyper(f'{time_date}, {exact_time}')
                title = element.find('h2').text
                url = element.find('a')['href'].replace('//m.', '//')
                url_parsed = urlparse(url)
                url_res = f'{url_parsed.scheme}://{url_parsed.netloc}{url_parsed.path}'
                if title is None:
                    logging_fwa.warning(f'Заголовок пустой. Url: {url}\n')
                    continue
                if not News.objects.filter(source=url_res).exists():
                    News.objects.create(
                        date=news_exact_time,
                        team=team_q,
                        title=title,
                        source=url_res)
                    short_counter += 1
                    logging_fwa.info(f'Добавленая блоговая новость {url_res}')
        logging_fwa.info(f'{short_counter} коротких новостей добавлены для команды {team_name}')
    except OperationalError as doe:
        logging_fwa.error(f'Поймали {doe}\nПробуем еще раз')
        time.sleep(1)
