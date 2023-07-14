from django.shortcuts import render
from .models import News, Teams, StatEpl, GoalscorersEPL, AssistantsEPL, CalendarMatches


def index(request):
    if request.GET:
        team_1 = Teams.objects.get(name=request.GET['team_name'])
    else:
        team_1 = Teams.objects.get(name='Арсенал')
    upcoming_event = CalendarMatches.objects.filter(match_score='превью', team=team_1).order_by('date_match').first()
    team_2 = upcoming_event.rival
    qty = 5
    season = '2022/2023'

    context = {
        'season': season,
        'team_1': team_1,
        'team_2': team_2,
        'news_1': News.objects.filter(team=team_1).order_by('-date')[:qty],
        'news_2': News.objects.filter(team=team_2).order_by('-date')[:qty],
        'stats': StatEpl.objects.all(),
        'stats_1': StatEpl.objects.filter(team=team_1).first(),
        'stats_2': StatEpl.objects.filter(team=team_2).first(),
        'goalscorers': GoalscorersEPL.objects.all(),
        'goalscorers_1': GoalscorersEPL.objects.filter(team=team_1).order_by('position')[:3],
        'goalscorers_1_qty': len(GoalscorersEPL.objects.filter(team=team_1).order_by('position')[:3]) + 1,
        'goalscorers_2': GoalscorersEPL.objects.filter(team=team_2).order_by('position')[:3],
        'goalscorers_2_qty': len(GoalscorersEPL.objects.filter(team=team_2).order_by('position')[:3]) + 1,
        'assistants': AssistantsEPL.objects.all(),
        'assistants_1': AssistantsEPL.objects.filter(team=team_1).order_by('position')[:3],
        'assistants_1_qty': len(AssistantsEPL.objects.filter(team=team_1).order_by('position')[:3]) + 1,
        'assistants_2': AssistantsEPL.objects.filter(team=team_2).order_by('position')[:3],
        'assistants_2_qty': len(AssistantsEPL.objects.filter(team=team_2).order_by('position')[:3]) + 1,
        'matches': CalendarMatches.objects.all(),
        'teams': Teams.objects.filter(league='АПЛ').order_by('name'),
        'tournament': upcoming_event.tournament,
        'date': upcoming_event.date_match,
    }

    return render(request, 'fwa/index.html', context)


def news(request):
    team_1 = Teams.objects.get(name=request.GET['team_name'])
    team_2 = CalendarMatches.objects.filter(match_score='превью', team=team_1).order_by('date_match').first().rival
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
    team_2 = CalendarMatches.objects.filter(match_score='превью', team=team_1).order_by('date_match').first().rival

    context = {
        'season': season,
        'stats': StatEpl.objects.filter(season=season).order_by('position'),
        'team_1': team_1,
        'team_2': team_2,
    }

    return render(request, 'fwa/stats.html', context)


def goalscorers(request):
    season = '2022/2023'
    team_1 = Teams.objects.get(name=request.GET['team_name'])
    team_2 = CalendarMatches.objects.filter(match_score='превью', team=team_1).order_by('date_match').first().rival

    context = {
        'season': season,
        'goalscorers': GoalscorersEPL.objects.filter(season=season).order_by('position'),
        'team_1': team_1,
        'team_2': team_2,
    }

    return render(request, 'fwa/goalscorers.html', context)


def assistants(request):
    season = '2022/2023'
    team_1 = Teams.objects.get(name=request.GET['team_name'])
    team_2 = CalendarMatches.objects.filter(match_score='превью', team=team_1).order_by('date_match').first().rival

    context = {
        'season': season,
        'assistants': AssistantsEPL.objects.filter(season=season).order_by('position'),
        'team_1': team_1,
        'team_2': team_2,
    }

    return render(request, 'fwa/assistants.html', context)


def calendar(request):
    season = '2023/2024'
    team_1 = Teams.objects.get(name=request.GET['team_name'])
    team_2 = CalendarMatches.objects.filter(match_score='превью', team=team_1).order_by('date_match').first().rival

    context = {
        'season': season,
        'calendar': CalendarMatches.objects.filter(team=team_1, season=season).order_by('date_match'),
        'team_1': team_1,
        'team_2': team_2,
    }

    return render(request, 'fwa/calendar.html', context)
