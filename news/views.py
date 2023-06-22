from django.shortcuts import render
from .models import News, StatEpl, GoalscorersEPL, AssistentsEPL


def index(request):
    context = {
        'news': News.objects.all()
    }
    return render(request, 'news/index.html', context)


def statistics(request):
    context = {
        'stats': StatEpl.objects.all(),
    }
    return render(request, 'news/parses.html', context)


def goalscorers_epl(request):
    context = {
        'goalscorers': GoalscorersEPL.objects.all(),
    }
    return render(request, 'news/parses.html', context)


def assistents_epl(request):
    context = {
        'assistents': AssistentsEPL.objects.all(),
    }
    return render(request, 'news/parses.html', context)
