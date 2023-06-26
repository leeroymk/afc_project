from django.shortcuts import render
from .models import News, Teams, StatEpl, GoalscorersEPL, AssistentsEPL, CalendarMatches


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


def statistics(request):
    context = {
        'stats': StatEpl.objects.all(),
    }
    return render(request, 'fwa/parses.html', context)


def goalscorers_epl(request):
    context = {
        'goalscorers': GoalscorersEPL.objects.all(),
    }
    return render(request, 'fwa/parses.html', context)


def assistents_epl(request):
    context = {
        'assistents': AssistentsEPL.objects.all(),
    }
    return render(request, 'fwa/parses.html', context)


def calendar(request):
    context = {
        'matches': CalendarMatches.objects.all(),
    }
    return render(request, 'fwa/parses.html', context)
