from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index-page'),
    path('stats/', views.statistics, name='stats-page'),
]
