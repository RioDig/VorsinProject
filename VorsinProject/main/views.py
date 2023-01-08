from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from .scripts import API_Requests, SQL_Analytics_Requests
import re
import jinja2


def index(request):
    return render(request, 'main/index.html')


def recent_vacancies(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        vacancies_data = API_Requests.get_vacancies(day)
        if vacancies_data is not None:
            context = {'data': vacancies_data}
            return render(request, 'main/recent_vacancies.html', context=context)
        else:
            messages.error(request, 'Ничего не найдено')
        return render(request, 'main/recent_vacancies.html')
    return render(request, 'main/recent_vacancies.html')


def demand_vacancies(request):
    if request.method == 'POST':
        key_words = request.POST.get('key_words')
        pattern = re.compile("^[a-zA-Zа-яА-ЯёЁ+ ]+$")
        if pattern.search(key_words) is not None:
            try:
                key_words = key_words.split('+')
            except:
                messages.error(request, 'Ошибка при вводе ключевых слов')
                return render(request, 'main/demand_vacancies.html')
            sql_response = SQL_Analytics_Requests.get_demand_analytics(key_words)
            tokens = sql_response['tokens']
            return render(request, 'main/demand_vacancies.html',
                          context={'fig1': tokens[0], 'fig2': tokens[1], 'key_words': key_words, 'data': sql_response['data']})
        else:
            messages.error(request, 'Вы ввели неверные ключевые слова')
            return render(request, 'main/demand_vacancies.html')
    return render(request, 'main/demand_vacancies.html')


def geo_vacancies(request):
    if request.method == 'POST':
        key_words = request.POST.get('key_words')
        area_name = request.POST.get('area_name')
        pattern = re.compile("^[a-zA-Zа-яА-ЯёЁ+ ]+$")
        if pattern.search(key_words) is not None and pattern.search(area_name) is not None:
            try:
                key_words = key_words.split('+')
            except:
                messages.error(request, 'Ошибка при вводе ключевых слов')
                return render(request, 'main/geo_vacancies.html')
            sql_response = SQL_Analytics_Requests.get_geo_analytics(key_words, area_name)
            tokens = sql_response['data']
            return render(request, 'main/geo_vacancies.html',
                          context={'fig1': tokens[0], 'fig2': tokens[1], 'fig3': tokens[2], 'fig4': tokens[3], 'area_name': area_name, 'key_words': key_words,
                                   'data': sql_response['year_analysis'], 'area_analysis_salary': sql_response['area_analysis_salary'], 'area_analysis_fraction': sql_response['area_analysis_fraction']})
        else:
            messages.error(request, 'Вы ввели неверные ключевые слова или город')
            return render(request, 'main/geo_vacancies.html')
    return render(request, 'main/geo_vacancies.html')