import datetime

import requests
import re


def clean_html(raw_html: str) -> str:
    """
    Выполняет чистку строки от HTML-тегов и лишних специальных символов.

    :param raw_html: Исходная строка данных
    :return: Возвращает универсальную строку для обработки
    """
    clean_text = re.sub('<.*?>', '', raw_html).replace('\r\n', ' ').replace(u'\xa0', ' ').replace(u'\u2002',
                                                                                                  ' ').strip()
    return re.sub(' +', ' ', clean_text)


def valute_formatter(raw_str: dict) -> str:
    valutes = {
        "AZN": "Манаты",
        "BYR": "Белорусские рубли",
        "EUR": "Евро",
        "GEL": "Грузинский лари",
        "KGS": "Киргизский сом",
        "KZT": "Тенге",
        "RUR": "Рубли",
        "UAH": "Гривны",
        "USD": "Доллары",
        "UZS": "Узбекский сум",
    }
    return f"{int((int(raw_str['salary']['from'] or 0) + int(raw_str['salary']['to'] or 0)) / 2):,} " \
           f"{raw_str['salary']['currency']} ({valutes[raw_str['salary']['currency']]})"


def skills_formatter(raw_skills: list) -> str:
    return ', '.join([skill['name'] for skill in raw_skills])


def parse_date(date):
    return datetime.datetime.strptime(date.replace('T', ' ')[:18], '%Y-%m-%d %H:%M:%S')


def get_vacancies(date: str):
    if len(date.split('-')) == 2:
        vacancies = requests.get(
            f'https://api.hh.ru/vacancies?specialization=1&'
            f'date_from={date}-01T00:00:00&'
            f'date_to={date}-28T23:59:59&'
            f'text=NAME:(game+OR+unity+OR+игр+OR+unreal+OR+гейм)&'
            f'only_with_salary=true&'
            f'order_by=publication_time&'
            f'per_page=10').json()['items']
    else:
        vacancies = requests.get(
            f'https://api.hh.ru/vacancies?specialization=1&'
            f'date_from={date}T00:00:00&'
            f'date_to={date}T23:59:59&'
            f'text=NAME:(game+OR+unity+OR+игр+OR+unreal+OR+гейм)&'
            f'only_with_salary=true&'
            f'order_by=publication_time&'
            f'per_page=10').json()['items']

    if len(vacancies) > 0:
        vacancies_full = [requests.get(f'https://api.hh.ru/vacancies/{vacancy["id"]}').json() for vacancy in vacancies]

        formatted_vacancies = []
        for vacancy in vacancies_full:
            vacancy_info = {
                'name': vacancy['name'],
                'description': clean_html(vacancy['description']),
                'key_skills': skills_formatter(vacancy['key_skills']),
                'company': vacancy['employer']['name'],
                'salary': valute_formatter(vacancy),
                'area_name': vacancy['area']['name'],
                'published_at': parse_date(vacancy['published_at'])
            }
            formatted_vacancies.append(vacancy_info)

        return formatted_vacancies
    return None
