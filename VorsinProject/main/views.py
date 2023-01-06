import requests
from django.shortcuts import render, redirect
from django.contrib import messages
import re
import datetime

def index(request):
    return render(request, 'main/index.html')



def clean_html(raw_html: str) -> str:
    """
    Выполняет чистку строки от HTML-тегов и лишних специальных символов.

    :param raw_html: Исходная строка данных
    :return: Возвращает универсальную строку для обработки
    """
    clean_text = re.sub('<.*?>', '', raw_html).replace('\r\n', ' ').replace(u'\xa0', ' ').replace(u'\u2002',
                                                                                                  ' ').strip()
    return re.sub(' +', ' ', clean_text)

def datetime_formatter(raw_date: str) -> str:
    months = {
        '1': 'Января',
        '2': 'Февраля',
        '3': 'Марта',
        '4': 'Апреля',
        '5': 'Мая',
        '6': 'Июня',
        '7': 'Июля',
        '8': 'Августа',
        '9': 'Сентября',
        '10': 'Октября',
        '11': 'Ноября',
        '12': 'Декабря',
    }
    date = datetime.datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S%z').date()
    return f'{date.day} {months[str(date.month)]} {date.year} г.'

def recent_vacancies(request):
    if request.method == 'POST':
        day = request.POST.get('day')

        if len(day.split('-')) == 2:
            vacancies = requests.get(
                f'https://api.hh.ru/vacancies?specialization=1&date_from={day}-01T00:00:00&date_to={day}-28T23:59:59&text=NAME:(game+OR+unity+OR+игр+OR+unreal+OR+гейм)&only_with_salary=true&order_by=publication_time&per_page=10').json()['items']
        else:
            vacancies = requests.get(
                f'https://api.hh.ru/vacancies?specialization=1&date_from={day}T00:00:00&date_to={day}T23:59:59&text=NAME:(game+OR+unity+OR+игр+OR+unreal+OR+гейм)&only_with_salary=true&order_by=publication_time&per_page=10').json()['items']

        if len(vacancies) > 0:
            test = []
            for vacancy in vacancies:
                test.append(requests.get(f'https://api.hh.ru/vacancies/{vacancy["id"]}').json())


            mas = []
            for vac in test:
                vacancy_info = {'name': vac['name'],
                                'description': clean_html(vac['description']),
                                'key_skills': vac['key_skills'],
                                'company': vac['employer']['name'],
                                'salary': str((int(vac['salary']['from'] or 0) + int(vac['salary']['to'] or 0)) / 2) + vac['salary']['currency'],
                                'area_name': vac['area']['name'],
                                'published_at': datetime_formatter(vac['published_at'])}
                mas.append(vacancy_info)

            context = {'data': mas}

            return render(request, 'main/test.html', context=context)





        else:
            messages.error(request, 'Ничего не найдено')
        return render(request, 'main/test.html')

    return render(request, 'main/test.html')

