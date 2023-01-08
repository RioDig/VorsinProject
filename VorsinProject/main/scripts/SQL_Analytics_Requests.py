import base64
import io
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
from typing import Dict, Any, List
from matplotlib import pyplot as plt, cm

matplotlib.use('Agg')


def sort_dict_area(unsorted_dict: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Метод для сортировки словаря по городам вакансии

    :param unsorted_dict: Исходный словарь
    :return: Возвращает отсортированный словарь
    """
    sorted_tuples = sorted(unsorted_dict.items(), key=lambda item: item[1], reverse=True)[:10]
    sorted_dict = {key: value for key, value in sorted_tuples}
    return sorted_dict


connect = sqlite3.connect("db.sqlite3", check_same_thread=False)
template_dict = {'2003': 0, '2004': 0, '2005': 0, '2006': 0, '2007': 0, '2008': 0, '2009': 0, '2010': 0, '2011': 0,
                 '2012': 0, '2013': 0, '2014': 0, '2015': 0, '2016': 0, '2017': 0, '2018': 0, '2019': 0, '2020': 0,
                 '2021': 0, '2022': 0}


def generate_base64_token(graph) -> str:
    """
    Метод для создания токена графика

    :param graph: Передаваемый график
    :return: Возвращает токен в формате строки
    """
    flike = io.BytesIO()
    graph.savefig(flike)
    return base64.b64encode(flike.getvalue()).decode()


def generate_image_demand(year_analytics_dicts: List) -> List[str]:
    """
    Метод для генерации .png графиков с аналитикой в раздел "Востребованность"

    :param year_analytics_dicts: Словари с аналитикой по годам для всех профессий и для выбранной профессии
    :returns: Возвращает список токенов графиков для дальнейшего использования в HTML-шаблоне
    """
    graph1 = plt.figure()
    width = 0.4
    x_axis = np.arange(len(year_analytics_dicts[0].keys()))

    first_graph = graph1.add_subplot()
    first_graph.set_title("Уровень зарплат по годам")
    first_graph.bar(x_axis - width / 2, year_analytics_dicts[0].values(), width, label="средняя з/п")
    first_graph.bar(x_axis + width / 2, year_analytics_dicts[1].values(), width,
                    label=f"з/п по выбранной профессии")
    first_graph.set_xticks(x_axis, year_analytics_dicts[0].keys(), rotation="vertical")
    first_graph.tick_params(axis="both", labelsize=8)
    first_graph.legend(fontsize=8)
    first_graph.grid(True, axis="y")
    plt.tight_layout()
    b64_1 = generate_base64_token(graph1)

    graph2 = plt.figure()
    second_graph = graph2.add_subplot()
    second_graph.set_title("Количество вакансий по годам")
    second_graph.bar(x_axis - width / 2, year_analytics_dicts[2].values(), width,
                     label="Количество вакансий по всем профессиям")
    second_graph.bar(x_axis + width / 2, year_analytics_dicts[3].values(), width,
                     label=f"Количество вакансий по выбранной профессии")
    second_graph.set_xticks(x_axis, year_analytics_dicts[2].keys(), rotation="vertical")
    second_graph.tick_params(axis="both", labelsize=8)
    second_graph.legend(fontsize=8)
    second_graph.grid(True, axis="y")
    plt.tight_layout()
    b64_2 = generate_base64_token(graph2)

    return [b64_1, b64_2]


def get_demand_analytics(key_words: List[str]) -> Dict:
    """
    Метод для создания запросов к Базе данных для получения аналитики по востребованности определенной профессии

    :param key_words: Ключевые слова профессии
    :return: Возвращает токены на графики аналитики
    """
    prof_year_salary_sql = "SELECT SUBSTR(published_at, 1, 4) AS year, ROUND(AVG(salary)) FROM 'vacancy_db.sqlite' WHERE "
    prof_year_vacancy_sql = "SELECT SUBSTR(published_at, 1, 4) AS year, COUNT(name) FROM 'vacancy_db.sqlite' WHERE "
    for i in range(0, len(key_words)):
        if i == len(key_words) - 1:
            prof_year_salary_sql += f"name LIKE '%{key_words[i]}%' "
            prof_year_vacancy_sql += f"name LIKE '%{key_words[i]}%' "
            break
        prof_year_salary_sql += f"name LIKE '%{key_words[i]}%' OR "
        prof_year_vacancy_sql += f"name LIKE '%{key_words[i]}%' OR "
    prof_year_salary_sql += "GROUP BY year"
    prof_year_vacancy_sql += "GROUP BY year"

    year_salary_groups = pd.read_sql(
        "SELECT SUBSTR(published_at, 1, 4) AS year, ROUND(AVG(salary)) FROM 'vacancy_db.sqlite' GROUP BY year", connect)
    year_salary_dict = dict(year_salary_groups[["year", "ROUND(AVG(salary))"]].to_dict("split")["data"])

    year_vacancy_groups = pd.read_sql(
        "SELECT SUBSTR(published_at, 1, 4) AS year, COUNT(name) FROM 'vacancy_db.sqlite' GROUP BY year", connect)
    year_vacancy_dict = dict(year_vacancy_groups[["year", "COUNT(name)"]].to_dict("split")["data"])

    profession_year_salary_groups = pd.read_sql(prof_year_salary_sql, connect)
    profession_year_salary_dict = {**template_dict, **dict(
        profession_year_salary_groups[["year", "ROUND(AVG(salary))"]].to_dict("split")["data"])}

    profession_year_vacancy_groups = pd.read_sql(prof_year_vacancy_sql, connect)
    profession_year_vacancy_dict = {**template_dict, **dict(
        profession_year_vacancy_groups[["year", "COUNT(name)"]].to_dict("split")["data"])}

    analytics_list = [year_salary_dict, profession_year_salary_dict, year_vacancy_dict, profession_year_vacancy_dict]

    analysis_list = []
    for key, value in analytics_list[0].items():
        analysis_list.append({'year': key, 'val0': value, 'val1': analytics_list[1][key], 'val2': analytics_list[2][key], 'val3': analytics_list[3][key]})
    return {'tokens': generate_image_demand(analytics_list), 'data': analysis_list}


def generate_image_geo(area_name: str, area_dicts: List[Dict], year_dicts: List[Dict]) -> List[str]:
    """
    Метод для генерации .png графиков с аналитикой в разделе "География"

    :param area_name: Название региона
    :param area_dicts: Список словарей по городам
    :param year_dicts: Список словарей по годам
    :returns: Возвращает список токенов графиков для дальнейшего использования в HTML-шаблоне
    """
    graph1 = plt.figure()
    width = 0.4
    x_axis = np.arange(len(year_dicts[0].keys()))

    first_graph = graph1.add_subplot()
    first_graph.set_title("Уровень зарплат по годам")
    first_graph.bar(x_axis, year_dicts[0].values(), width,
                    label=f"з/п по выбранным ключевым словам: {area_name.lower()}")
    first_graph.set_xticks(x_axis, year_dicts[0].keys(), rotation="vertical")
    first_graph.tick_params(axis="both", labelsize=8)
    first_graph.legend(fontsize=8)
    first_graph.grid(True, axis="y")
    plt.tight_layout()
    b64_1 = generate_base64_token(graph1)

    graph2 = plt.figure()
    second_graph = graph2.add_subplot()
    second_graph.set_title("Количество вакансий по годам")
    second_graph.bar(x_axis,
                     year_dicts[1].values(),
                     width,
                     label=f"Количество вакансий по выбранным ключевым словам: {area_name.lower()}")
    second_graph.set_xticks(x_axis, year_dicts[1].keys(), rotation="vertical")
    second_graph.tick_params(axis="both", labelsize=8)
    second_graph.legend(fontsize=8)
    second_graph.grid(True, axis="y")
    plt.tight_layout()
    b64_2 = generate_base64_token(graph2)

    graph3 = plt.figure()
    y_cities = np.arange(len(area_dicts[0].keys()))
    third_graph = graph3.add_subplot()
    third_graph.set_title("Уровень зарплат по городам")
    third_graph.barh(y_cities, area_dicts[0].values(), 0.8, align="center")
    third_graph.set_yticks(y_cities,
                           labels=[key.replace('-', '-\n').replace(' ', '\n') for key in area_dicts[0].keys()],
                           horizontalalignment="right",
                           verticalalignment="center")
    third_graph.tick_params(axis="x", labelsize=8)
    third_graph.tick_params(axis="y", labelsize=6)
    third_graph.invert_yaxis()
    third_graph.grid(True, axis="x")
    plt.tight_layout()
    b64_3 = generate_base64_token(graph3)

    graph4 = plt.figure()
    fourth_graph = graph4.add_subplot()
    fourth_graph.set_title("Доля вакансий по городам")
    area_dicts[1] = {'Другие': 1 - sum(area_dicts[1].values()), **area_dicts[1]}
    fourth_graph.pie(area_dicts[1].values(),
                     labels=area_dicts[1].keys(),
                     startangle=0,
                     textprops={'fontsize': 6},
                     colors=cm.Set3(np.arange(11)))
    fourth_graph.axis('equal')
    plt.tight_layout()
    b64_4 = generate_base64_token(graph4)

    return [b64_1, b64_2, b64_3, b64_4]


def get_geo_analytics(key_words: List[str], area_name: str):
    """
    Метод для создания запросов к Базе данных для получения аналитики по географии определенной профессии и города

    :param key_words: Ключевые слова по профессии
    :param area_name: Название города
    :return: Возвращает список токенов графиков аналитики
    """
    db_length = pd.read_sql("SELECT COUNT(*) FROM 'vacancy_db.sqlite'", connect).to_dict()["COUNT(*)"][0]
    prof_area_vacancy_salary = f"SELECT SUBSTR(published_at, 1, 4) AS year, ROUND(AVG(salary)) FROM 'vacancy_db.sqlite' WHERE (area_name == '{area_name}' AND ( "
    prof_area_vacancy_count = f"SELECT SUBSTR(published_at, 1, 4) AS year, COUNT(name) FROM 'vacancy_db.sqlite' WHERE (area_name == '{area_name}' AND ( "
    for i in range(0, len(key_words)):
        if i == len(key_words) - 1:
            prof_area_vacancy_salary += f"name LIKE '%{key_words[i]}%') "
            prof_area_vacancy_count += f"name LIKE '%{key_words[i]}%') "
            break
        prof_area_vacancy_salary += f"name LIKE '%{key_words[i]}%' OR "
        prof_area_vacancy_count += f"name LIKE '%{key_words[i]}%' OR "
    prof_area_vacancy_salary += " ) GROUP BY year"
    prof_area_vacancy_count += " ) GROUP BY year"

    area_salary_groups = pd.read_sql(
        "SELECT area_name, ROUND(AVG(salary)), COUNT(area_name) FROM 'vacancy_db.sqlite' "
        "GROUP BY area_name "
        "ORDER BY COUNT(area_name) DESC ", connect)
    area_salary_groups = area_salary_groups[area_salary_groups["COUNT(area_name)"] >= 0.01 * db_length]
    area_salary_dict = dict(area_salary_groups[["area_name", "ROUND(AVG(salary))"]].to_dict("split")["data"])
    area_salary_dict = sort_dict_area(area_salary_dict)

    area_vacancy_groups = pd.read_sql("SELECT area_name, COUNT(area_name) FROM 'vacancy_db.sqlite' "
                                      "GROUP BY area_name "
                                      "ORDER BY COUNT(area_name) DESC "
                                      "LIMIT 10", connect)
    area_vacancy_groups["COUNT(area_name)"] = round(area_vacancy_groups["COUNT(area_name)"] / db_length, 2)
    area_vacancy_dict = dict(area_vacancy_groups[["area_name", 'COUNT(area_name)']].to_dict("split")["data"])

    vacancy_area_salary = pd.read_sql(prof_area_vacancy_salary, connect)
    vacancy_area_salary = {**template_dict,
                           **dict(vacancy_area_salary[["year", "ROUND(AVG(salary))"]].to_dict("split")["data"])}

    vacancy_area_count = pd.read_sql(prof_area_vacancy_count, connect)
    vacancy_area_count = {**template_dict, **dict(vacancy_area_count[["year", "COUNT(name)"]].to_dict("split")["data"])}

    year_dicts = [vacancy_area_salary, vacancy_area_count]
    area_dicts = [area_salary_dict, area_vacancy_dict]

    year_analysis = []
    for key, value in year_dicts[0].items():
        year_analysis.append({'year': key, 'val0': value, 'val1': year_dicts[1][key]})

    area_analysis_salary = []
    for key, value in area_dicts[0].items():
        area_analysis_salary.append({'area': key, 'val0': value})

    area_analysis_fraction = []
    for key, value in area_dicts[1].items():
        area_analysis_fraction.append({'area': key, 'val0': value})

    return {'data': generate_image_geo(area_name, area_dicts, year_dicts), 'year_analysis': year_analysis,
            'area_analysis_salary': area_analysis_salary, 'area_analysis_fraction': area_analysis_fraction}
