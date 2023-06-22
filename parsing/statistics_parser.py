from pprint import pprint
from random import choice
import time
from bs4 import BeautifulSoup

import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options,
    )


def stats_parser(stats_page):
    for i in range(5):
        soup = BeautifulSoup(stats_page, 'lxml')
        stats_data = soup.find('table', class_='b-tag-tournament-stat__table g-table-b')
        headers = [header.text for header in stats_data.find_all('th')]
        if not headers:
            print(f'{i+1} try failed')
        else:
            tournament_data = []
            for row_data in stats_data.find_all('tr'):
                row = [', '.join(row_element.text.strip().split('\n')) for row_element in row_data.find_all('td')]
                tournament_data.append(row)
                metric_result = pd.DataFrame(tournament_data[1:], columns=headers)
                print(metric_result)
                return metric_result


def selenium_clicker(stats_url):
    # Выбираем сезон
    browser.get(stats_url)
    print('Мы в кликере')
    # element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'mdl-button mdl-js-button mdl-button--icon')))
    # btn_sel = '#section-stat-tournaments-list-button'
    more_btn = browser.find_element(By.CSS_SELECTOR, '#section-stat-tournaments-list-button')
    more_btn.click()

    time.sleep(1)
    # element.click()
    print('дропнули меню')


    select_season = browser.find_element(By.CLASS_NAME, 'selectpicker-15 show-menu-arrow')
    select = Select(select_season)
    select.select_by_visible_text("2022/2023")

    # Выбираем метрику
    browser.implicitly_wait(10)
    browser.find_element(By.CSS_SELECTOR, 'a[href="#pass"]').click()
    return browser.page_source


assists_page = selenium_clicker('https://m.bombardir.ru/england/stats')
# stats_parser(assists_page)

browser.quit()
