from db import db_session
from models import News

my_news = News.query.filter(News.id == 4).first()
db_session.delete(my_news)
db_session.commit()