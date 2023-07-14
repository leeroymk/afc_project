from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index-page'),
    path('news/', views.news, name='news-page'),
    path('stats/', views.stats, name='stats-page'),
    path('goalscorers/', views.goalscorers, name='goalscorers-page'),
    path('assistants/', views.assistants, name='assistants-page'),
    path('calendar/', views.calendar, name='calendar-page'),
]
