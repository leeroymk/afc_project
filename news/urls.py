from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index-page'),
    path('stats/', views.statistics, name='stats-page'),
    path('goals/', views.goalscorers_epl, name='bombardiers_epl'),
    path('assistents/', views.assistents_epl, name='assistents_epl'),
]
