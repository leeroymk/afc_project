from django.shortcuts import render
from .models import News, Teams, StatEpl, GoalscorersEPL, AssistentsEPL, CalendarMatches


def index(request):
    if request.GET:
        team_1 = Teams.objects.get(name=request.GET['team_name'])
    else:
        team_1 = Teams.objects.get(name='Арсенал')

    team_2 = Teams.objects.get(name='Челси')
    qty = 5

    context = {
        'team_1': team_1,
        'team_2': team_2,
        'news_1': News.objects.filter(team=team_1).order_by('-date')[:qty],
        'news_2': News.objects.filter(team=team_2).order_by('-date')[:qty],
        'stats': StatEpl.objects.all(),
        'stats_1': StatEpl.objects.filter(team=team_1).first(),
        'stats_2': StatEpl.objects.filter(team=team_2).first(),
        'goalscorers': GoalscorersEPL.objects.all(),
        'assistents': AssistentsEPL.objects.all(),
        'matches': CalendarMatches.objects.all(),
        'teams': Teams.objects.all().order_by('name'),
    }

    return render(request, 'fwa/index.html', context)


def news(request):
    team_1 = Teams.objects.get(name=request.GET['team_name'])
    team_2 = Teams.objects.get(name='Челси')
    qty = 25

    context = {
        'team_1': team_1,
        'team_2': team_2,
        'news_1': News.objects.filter(team=team_1).order_by('-date')[:qty],
        'news_2': News.objects.filter(team=team_2).order_by('-date')[:qty],
    }

    return render(request, 'fwa/news.html', context)


def stats(request):
    season = '2022/2023'
    team_1 = Teams.objects.get(name=request.GET['team_name'])
    team_2 = Teams.objects.get(name='Челси')

    context = {
        'season': season,
        'stats': StatEpl.objects.filter(season=season).order_by('position'),
        'team_1': team_1,
        'team_2': team_2,
    }

    return render(request, 'fwa/stats.html', context)
