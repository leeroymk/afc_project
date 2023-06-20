from django.shortcuts import render
from .models import News, StatEpl


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
