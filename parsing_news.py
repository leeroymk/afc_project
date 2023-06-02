from pprint import pprint
import requests
import lxml
from bs4 import BeautifulSoup


# Код пока не показывает время новости, также парсит только видимую страницу
# следующий фрагмент открывается только при прокрутке мышью

def get_html(url):
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.text
    except (requests.RequestException, ValueError):
        print('Сетевая ошибка')
        return False
    
def get_arsenal_news():
    with open("arsenal_news.html", "r", encoding="utf8") as f:
        html = f.read()    
        
    soup = BeautifulSoup(html, 'lxml')
    short_news = soup.find_all('p')
    bold_news = soup.find_all(class_='titleH2')
    result_news = []
    for snew in short_news:
        try:
            title = snew.find('a').text
            url = snew.find('a')['href']
        except (TypeError, AttributeError):
            continue
        result_news.append({
            'title': title,
            'url': url,
            })
    for bnew in bold_news:
        title = bnew.find('a').text
        url = bnew.find('a')['href']
        result_news.append({
            'title': title,
            'url': url,
        })

    pprint(result_news)
    return result_news


if __name__ == "__main__":
    html = get_html("https://www.sports.ru/arsenal/")
    if html:
        with open("arsenal_news.html", "w", encoding="utf8") as f:
            f.write(html)
get_arsenal_news()
