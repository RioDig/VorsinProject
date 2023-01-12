from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('recent_vacancies/', views.recent_vacancies, name='recent_vacancies'),
    path('demand_vacancies/', views.demand_vacancies, name='demand_vacancies'),
    path('geo_vacancies/', views.geo_vacancies, name='geo_vacancies'),
    path('skills/', views.skills, name='skills'),
]
