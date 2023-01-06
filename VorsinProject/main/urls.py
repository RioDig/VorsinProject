from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('recent_vacancies/', views.recent_vacancies, name='recent_vacancies'),
]
