from django.shortcuts import render
from .models import News

news = []

for one_news in News.objects.all():
    news.append(
        f"id: {one_news.id}, date: {one_news.news_date}, title: {one_news.news_title}, context: {one_news.news_context}, source: {one_news.news_source}")


def home(request):
    context = {
        'news': news
    }
    return render(request, 'news/home.html', context)
