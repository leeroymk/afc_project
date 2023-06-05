import requests
import lxml
from bs4 import BeautifulSoup
from random import choice


def get_html(url):
    try:
        result = requests.get(url, headers=random_headers())
        result.raise_for_status()
        return result.text
    except (requests.RequestException, ValueError):
        print('Сетевая ошибка')
        return False


def get_team_news(club_link):
    club_src = requests.get(club_link, headers=random_headers())
    # Тут возможно нужна проверка raise_for_status()
    soup = BeautifulSoup(club_src.text, 'lxml')
    short_news = soup.find_all(class_='b-tag-lenta__item-news-item')
    bold_news = soup.find_all(class_='b-tag-lenta__item-body')
    result_news = []
    for snew in short_news:
        try:
            title = snew.find('h2').text
            url = snew.find('a')['href']
        except (TypeError, AttributeError) as er:
            print(f'Something wrong here: {er}')
            continue
        result_news.append({
            'title': title,
            'url': url,
            })
    for bnew in bold_news:
        title = bnew.find('h2').text
        url = bnew.find('a')['href']
        result_news.append({
            'title': title,
            'url': url,
        })
    return result_news


def get_teams_list(src):
    soup = BeautifulSoup(src, 'lxml')
    teams_list = soup.find_all(class_='b-tag-table__content-team')
    teams_data = {}
    # Создаем словарь, добавляем ссылки к ключам-названиям команды
    for team in teams_list:
        teams_data.update(
            {
                team.find('a').text: {
                    'url': team.find('a')['href'],
                }
            }
        )
    # Наполняем словарь новостями о каждой команде лиги
    for team in teams_list:
        team_name = team.find('a').text
        teams_data.update(
            {
                team_name: {
                    'club_news': get_team_news(teams_data[team_name]['url'])
                }
            }
        )

    return print('Done!')


if __name__ == "__main__":
    desktop_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        ]

    def random_headers():
        return {'Accept': '*/*',
                'User-Agent': choice(desktop_agents),
                }

    html = get_html('https://m.sports.ru/epl/table/')
    if html:
        get_teams_list(html)
    else:
        print('Wrong way')