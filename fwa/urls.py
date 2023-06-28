from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index-page'),
    path('news/', views.news, name='news-page'),
]
