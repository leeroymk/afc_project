from django.shortcuts import render
from .models import News

#  TODO: ограничить длину заголовка 197 символами + '...'. Наполнять проблеами (мб), если длина короче.
# Создать  промежуточный словарь


def index(request):
    team_1 = 'Арсенал'
    team_2 = 'Манчестер Сити'
    qty = 5

    news = []
    for item in News.objects.filter(team=team_1).order_by('-date')[:qty]:
        news.append([item])

    counter = 0
    for item in News.objects.filter(team=team_2).order_by('-date')[:qty]:
        news[counter].append(item)
        counter += 1

    context = {
        'team_1': team_1,
        'team_2': team_2,
        'news_1': News.objects.filter(team=team_1).order_by('-date')[:qty],
        'news_2': News.objects.filter(team=team_2).order_by('-date')[:qty],
        'teams': [team_1, team_2],
        'news': news,
    }
    return render(request, 'news/index.html', context)


def test(request):
    team_1 = 'Арсенал'
    team_2 = 'Манчестер Сити'
    qty = 5

    news = []
    for item in News.objects.filter(team=team_1).order_by('-date')[:qty]:
        news.append([item])

    counter = 0
    for item in News.objects.filter(team=team_2).order_by('-date')[:qty]:
        news[counter].append(item)
        counter += 1

    context = {
        'team_1': team_1,
        'team_2': team_2,
        'news_1': News.objects.filter(team=team_1).order_by('-date')[:qty],
        'news_2': News.objects.filter(team=team_2).order_by('-date')[:qty],
        'teams': [team_1, team_2],
        'news': news,
    }

    return render(request, 'news/test.html', context)
