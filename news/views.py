from django.shortcuts import render
from .get_news import news_all

# news = '\n'.join(f"id: {one_news.id}, Дата: {one_news.date}, Новость: {one_news.news_title}, Источник: {one_news.news_source}" for one_news in news_all)
# print(news)

news = []
for one_news in news_all:
    news.append(f"id: {one_news.id}, Дата: {one_news.date}, Новость: {one_news.news_title}, Источник: {one_news.news_source}")

def home(request):
    context = {
        'news': news
    }
    return render(request, 'news/home.html', context)
