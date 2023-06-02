from .models import News

my_news = News.query.filter(News.id == 3).first()
print(my_news)

news_all = News.query.all()
for one_news in news_all:
    print(f"""id: {one_news.id}
Дата: {one_news.date}
Новость: {one_news.news_title}
Источник: {one_news.news_source}
""")
