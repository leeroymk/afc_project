from db import db_session
from models import News

my_news = News.query.first()
my_news.news_source = 'Somewhere'
db_session.commit()