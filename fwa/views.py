from django.shortcuts import render
from .models import News, Teams


def index(request):
    team_1 = 'Арсенал'
    team_2 = 'Манчестер Сити'
    qty = 5

    context = {
        'team_1': team_1,
        'team_2': team_2,
        'news_1': News.objects.filter(team=Teams.objects.filter(name=team_1).first().id).order_by('-date')[:qty],
        'news_2': News.objects.filter(team=Teams.objects.filter(name=team_2).first().id).order_by('-date')[:qty],
    }

    return render(request, 'fwa/index.html', context)
