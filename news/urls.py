from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index-page'),
    path('test/', views.test, name='test-page'),
    
]
