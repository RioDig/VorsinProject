from django.shortcuts import render
from django.contrib import messages
from .scripts import API_Requests


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

