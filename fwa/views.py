from django.shortcuts import render
from .models import News, Teams, StatEpl, GoalscorersEPL, AssistentsEPL, CalendarMatches


def index(request):
    if request.GET:
        team_1 = request.GET['team_name']
        team_2 = 'Манчестер Сити'
        qty = 5

        context = {
            'team_1': team_1,
            'team_2': team_2,
            'logo_1': Teams.objects.get(name=team_1).logo,
            'logo_2': Teams.objects.get(name=team_2).logo,
            'news_1': News.objects.filter(team=Teams.objects.get(name=team_1).id).order_by('-date')[:qty],
            'news_2': News.objects.filter(team=Teams.objects.get(name=team_2).id).order_by('-date')[:qty],
            'stats': StatEpl.objects.all(),
            'stats_1': StatEpl.objects.get(team=Teams.objects.get(name=team_1).id),
            'stats_2': StatEpl.objects.get(team=Teams.objects.get(name=team_2).id),
            'goalscorers': GoalscorersEPL.objects.all(),
            'assistents': AssistentsEPL.objects.all(),
            'matches': CalendarMatches.objects.all(),
            'getreq': f'?team_name={team_1}',
        }

        return render(request, 'fwa/index.html', context)
    else:
        context = {
            'teams': Teams.objects.all().order_by('name'),
        }

        return render(request, 'fwa/choose_team.html', context)


def news(request):
    team_1 = request.GET['team_name']
    team_2 = 'Манчестер Сити'
    qty = 25

    context = {
        'team_1': team_1,
        'team_2': team_2,
        'news_1': News.objects.filter(team=Teams.objects.filter(name=team_1).first().id).order_by('-date')[:qty],
        'news_2': News.objects.filter(team=Teams.objects.filter(name=team_2).first().id).order_by('-date')[:qty],
        'getreq': f'?team_name={team_1}',
    }

    return render(request, 'fwa/news.html', context)


def stats(request):
    season = '2022/2023'
    team_1 = request.GET['team_name']

    context = {
        'season': season,
        'stats': StatEpl.objects.filter(season=season).order_by('position'),
        'team_1': team_1,
        'getreq': f'?team_name={team_1}',
    }

    return render(request, 'fwa/stats.html', context)
