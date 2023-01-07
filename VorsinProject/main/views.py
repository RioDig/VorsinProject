from django.shortcuts import render
from django.contrib import messages
from .scripts import API_Requests, SQL_Analytics_Requests

import base64
import io
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('Agg')


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
        try:
            key_words = key_words.split('+')
        except:
            messages.error(request, 'Ошибка при вводе ключевых слов')
            return render(request, 'main/demand_vacancies.html')
        tokens = SQL_Analytics_Requests.get_demand_analytics(key_words)
        return render(request, 'main/demand_vacancies.html', context={'fig1': tokens[0], 'fig2': tokens[1]})
    return render(request, 'main/demand_vacancies.html')


def geo_vacancies(request):
    if request.method == 'POST':
        key_words = request.POST.get('key_words')
        area_name = request.POST.get('area_name')
        try:
            key_words = key_words.split('+')
        except:
            messages.error(request, 'Ошибка при вводе ключевых слов')
            return render(request, 'main/geo_vacancies.html')
        tokens = SQL_Analytics_Requests.get_geo_analytics(key_words, area_name)
        return render(request, 'main/geo_vacancies.html', context={'fig1': tokens[0], 'fig2': tokens[1], 'fig3': tokens[2], 'fig4': tokens[3]})
    return render(request, 'main/geo_vacancies.html')