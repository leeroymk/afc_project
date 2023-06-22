from django.shortcuts import render, HttpResponse
from .models import News


def index(request):
    team_1 = 'Арсенал'
    team_2 = 'Манчестер Сити'
    qty = 5

    context = {
        'team_1': team_1,
        'team_2': team_2,
        'news_1': News.objects.filter(team=team_1).order_by('-date')[:qty],
        'news_2': News.objects.filter(team=team_2).order_by('-date')[:qty],
    }

    return render(request, 'news/index.html', context)
