from db import db_session
from models import News

first_news = News(date='01.06.2023',
                  news_title='We won',
                  news_context='We have just an outstanding game',
                  news_source='My phone')
second_news = News(date='02.06.2023',
                   news_title='We won again',
                   news_context='We have just another outstanding game',
                   news_source='Telegram')
db_session.add(first_news)
db_session.add(second_news)
db_session.commit()