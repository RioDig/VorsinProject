import base64
import io
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
from typing import Dict, Any
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
ultimate_dict = {'2003': 0, '2004': 0, '2005': 0, '2006': 0, '2007': 0, '2008': 0, '2009': 0, '2010': 0, '2011': 0,
                 '2012': 0, '2013': 0, '2014': 0, '2015': 0, '2016': 0, '2017': 0, '2018': 0, '2019': 0, '2020': 0,
                 '2021': 0, '2022': 0}


def generate_image(year_analytics_dicts):
    """
    Метод для генерации .png графиков с аналитикой по годам

    :param profession_name: Название профессии
    :param year_analytics_dicts: Словари с аналитикой по годам для всех профессий и для выбранной профессии
    """
    graph = plt.figure()
    width = 0.4
    x_axis = np.arange(len(year_analytics_dicts[0].keys()))

    first_graph = graph.add_subplot()
    first_graph.set_title("Уровень зарплат по годам")
    first_graph.bar(x_axis - width / 2, year_analytics_dicts[0].values(), width, label="средняя з/п")
    first_graph.bar(x_axis + width / 2, year_analytics_dicts[1].values(), width,
                    label=f"з/п по выбранной профессии")
    first_graph.set_xticks(x_axis, year_analytics_dicts[0].keys(), rotation="vertical")
    first_graph.tick_params(axis="both", labelsize=8)
    first_graph.legend(fontsize=8)
    first_graph.grid(True, axis="y")
    plt.tight_layout()

    flike = io.BytesIO()
    graph.savefig(flike)
    b64_1 = base64.b64encode(flike.getvalue()).decode()

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
    flike2 = io.BytesIO()
    graph2.savefig(flike2)
    b64_2 = base64.b64encode(flike2.getvalue()).decode()
    return [b64_1, b64_2]

def get_demand_analytics(key_words):
    pr = "SELECT SUBSTR(published_at, 1, 4) AS year, ROUND(AVG(salary)) FROM 'vacancy_db.sqlite' WHERE "
    pv = "SELECT SUBSTR(published_at, 1, 4) AS year, COUNT(name) FROM 'vacancy_db.sqlite' WHERE "
    for i in range(0, len(key_words)):
        if i == len(key_words) - 1:
            pr += f"name LIKE '%{key_words[i]}%' "
            pv += f"name LIKE '%{key_words[i]}%' "
            break
        pr += f"name LIKE '%{key_words[i]}%' OR "
        pv += f"name LIKE '%{key_words[i]}%' OR "
    pr += "GROUP BY year"
    pv += "GROUP BY year"

    year_salary_groups = pd.read_sql(
        "SELECT SUBSTR(published_at, 1, 4) AS year, ROUND(AVG(salary)) FROM 'vacancy_db.sqlite' GROUP BY year", connect)
    year_salary_dict = dict(year_salary_groups[["year", "ROUND(AVG(salary))"]].to_dict("split")["data"])

    year_vacancy_groups = pd.read_sql(
        "SELECT SUBSTR(published_at, 1, 4) AS year, COUNT(name) FROM 'vacancy_db.sqlite' GROUP BY year", connect)
    year_vacancy_dict = dict(year_vacancy_groups[["year", "COUNT(name)"]].to_dict("split")["data"])

    profession_year_salary_groups = pd.read_sql(pr, connect)
    profession_year_salary_dict = {**ultimate_dict, **dict(
        profession_year_salary_groups[["year", "ROUND(AVG(salary))"]].to_dict("split")["data"])}

    profession_year_vacancy_groups = pd.read_sql(pv, connect)
    profession_year_vacancy_dict = {**ultimate_dict, **dict(
        profession_year_vacancy_groups[["year", "COUNT(name)"]].to_dict("split")["data"])}

    analytics_list = [year_salary_dict, profession_year_salary_dict, year_vacancy_dict, profession_year_vacancy_dict]

    return generate_image(analytics_list)

def generate_image2(area_name, area_dicts, year_dicts):
    """
    Метод для генерации .png графиков с аналитикой по городам

    :param profession_name: Название профессии
    :param area_name: Название региона
    :param area_dicts: Список словарей по городам
    :param year_dicts: Список словарей по годам
    """
    graph = plt.figure()
    width = 0.4
    x_axis = np.arange(len(year_dicts[0].keys()))

    first_graph = graph.add_subplot()
    first_graph.set_title("Уровень зарплат по годам")
    first_graph.bar(x_axis, year_dicts[0].values(), width, label=f"з/п по выбранным ключевым словам в {area_name.lower()}")
    first_graph.set_xticks(x_axis, year_dicts[0].keys(), rotation="vertical")
    first_graph.tick_params(axis="both", labelsize=8)
    first_graph.legend(fontsize=8)
    first_graph.grid(True, axis="y")

    plt.tight_layout()
    flike1 = io.BytesIO()
    graph.savefig(flike1)
    b64_1 = base64.b64encode(flike1.getvalue()).decode()

    graph2 = plt.figure()
    second_graph = graph2.add_subplot()
    second_graph.set_title("Количество вакансий по годам")
    second_graph.bar(x_axis,
                     year_dicts[1].values(),
                     width,
                     label=f"Количество вакансий по выбранным ключевым словам в {area_name.lower()}")
    second_graph.set_xticks(x_axis, year_dicts[1].keys(), rotation="vertical")
    second_graph.tick_params(axis="both", labelsize=8)
    second_graph.legend(fontsize=8)
    second_graph.grid(True, axis="y")

    plt.tight_layout()
    flike2 = io.BytesIO()
    graph2.savefig(flike2)
    b64_2 = base64.b64encode(flike2.getvalue()).decode()

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
    flike3 = io.BytesIO()
    graph3.savefig(flike3)
    b64_3 = base64.b64encode(flike3.getvalue()).decode()

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
    flike1 = io.BytesIO()
    graph4.savefig(flike1)
    b64_4 = base64.b64encode(flike1.getvalue()).decode()
    return [b64_1, b64_2, b64_3, b64_4]

def get_geo_analytics(key_words, area_name):
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
    vacancy_area_salary = {**ultimate_dict,
                           **dict(vacancy_area_salary[["year", "ROUND(AVG(salary))"]].to_dict("split")["data"])}

    vacancy_area_count = pd.read_sql(prof_area_vacancy_count, connect)
    vacancy_area_count = {**ultimate_dict, **dict(vacancy_area_count[["year", "COUNT(name)"]].to_dict("split")["data"])}

    year_dicts = [vacancy_area_salary, vacancy_area_count]
    area_dicts = [area_salary_dict, area_vacancy_dict]

    return generate_image2(area_name, area_dicts, year_dicts)
