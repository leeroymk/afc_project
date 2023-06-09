from django.core.management.base import BaseCommand, CommandError
import logging
import requests
from random import choice
from news.models import News

import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Parse news'

    def handle(self, *args, **options):
        self.stdout.write("Test")

        # Проверяем URL на возможность соединения
        def get_html(url):
            try:
                result = requests.get(url, headers=random_headers())
                result.raise_for_status()
                return result.text
            except (requests.RequestException, ValueError):
                print('Сетевая ошибка')
                return False

        # Получаем список команд лиги
        def get_teams_list(html):
            soup = BeautifulSoup(html, 'lxml')
            teams_list = soup.find_all(class_='b-tag-table__content-team')
            # Добавляем ссылки к ключам-названиям команды
            for team in teams_list:
                teams_data.update(
                    {
                        team.find('a').text: {
                            'url': team.find('a')['href'],
                        }
                    }
                )
            return teams_list

        # Скроллим страницу
        def selenium_scroller(url):
            browser.get(url)
            try:
                # Здесь настраиваем количество страниц прокрутки
                for i in range(3):
                    btn_xpath = '//button[(contains(@class,"b-tag-lenta__show-more-button")) and(contains(text(),"Показать еще"))]'
                    more_btn = browser.find_element(By.XPATH, btn_xpath)
                    browser.execute_script("arguments[0].click();", more_btn)
            except (requests.RequestException, ValueError) as er:
                print(f'Ошибка {er} при парсинге {url}')
            finally:
                # Передаем в парсер новостей прокрученную страницу
                return get_team_news(browser.page_source)

        # Процесс парсинга новостей
        def get_team_news(scrolled_page):
            soup = BeautifulSoup(scrolled_page, 'lxml')
            parsed_news = []
            blog_news = soup.find_all(class_='b-tag-lenta__item m-type_blog')
            for bnew in blog_news:
                time_news = ''.join(
                    bnew.find(class_='b-tag-lenta__item-details').text).strip()
                title = bnew.find('h2').text
                url = bnew.find('a')['href']
                parsed_news.append(
                    {
                        'time': time_news,
                        'title': title,
                        'url': url,
                    })
            short_news = soup.find_all(class_='b-tag-lenta__item m-type_news')
            for snew in short_news:
                time_date = ''.join(
                    snew.find(class_='b-tag-lenta__item-details').text).strip()
                time_hours = snew.find_all(class_='b-tag-lenta__item-news-item')
                for element in time_hours:
                    exact_time = element.find('time').text
                    news_exact_time = f'{time_date}, {exact_time}'
                    title = element.find('h2').text
                    url = element.find('a')['href']
                    parsed_news.append(
                        {
                            'time': news_exact_time,
                            'title': title,
                            'url': url,
                        }
                    )
                    # __________________________________________________________________________________
                    n = News(date=news_exact_time, title=title, source=url)
                    n.save()
            # __________________________________________________________________________________
            return parsed_news

        logging.basicConfig(level=logging.INFO,
                            filename='log_parsing.log',
                            format="[%(asctime)s] %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
                            datefmt='%H:%M:%S',
                            )
        logging.debug("A DEBUG Message")
        logging.info("An INFO")
        logging.warning("A WARNING")
        logging.error("An ERROR")
        logging.critical("A message of CRITICAL severity")

        desktop_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPod; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; LM-Q710(FGN)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.60 Mobile Safari/537.36',

        ]

        def random_headers():
            return {'Accept': '*/*',
                    'User-Agent': choice(desktop_agents),
                    }

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )

        # Финальный словарь с новостями по каждой команде
        teams_data = {}

        teams_table = 'https://m.sports.ru/epl/table/'
        html = get_html(teams_table)
        if html:
            for team in get_teams_list(html):
                team_name = team.find('a').text
                teams_data.update(
                    {
                        # Парсим новости каждой команды (передаем URL в скроллер)
                        team_name: selenium_scroller(teams_data[team_name]['url'])
                    }
                )
        else:
            print('Что-то пошло не по плану...')

        browser.quit()
