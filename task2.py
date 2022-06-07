# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы
# получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать
# несколько страниц сайта (также вводим через input или аргументы). Получившийся список должен содержать в
# себе минимум:
# - Наименование вакансии.
# - Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# - Ссылку на саму вакансию.
# - Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
# одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas. Сохраните
# в json либо csv.

from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import json
import re
import pandas as pd

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/101.0.4951.64 Safari/537.36'}
job = 'Data science'
main_url = 'https://hh.ru'
page = 0
params = {'text': job,
          'from': 'suggest_post',
          'fromSearchLine': 'true',
          'area': 1002,
          'items_on_page': 20,
          'page': page}

response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)
# pprint(response.url)
soup = bs(response.text, 'html.parser')

pages = int(soup.find_all('a', {'class': 'bloko-button'})[-2].getText())
# pprint(pages)

for page in range(pages):
    soup = bs(response.text, 'html.parser')
    vacancies = (soup.find_all('div', {'class': 'vacancy-serp-item'}))
    # pprint(len(vacancies))

    all_vacancies = []

    for v in vacancies:
        v_data = {}

        v_name = v.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText()
        v_data['vacancy_name'] = v_name

        v_data['source'] = main_url

        v_link = v.find('a')['href']
        v_data['vacancy_link'] = v_link

        v_salary = v.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        # v_data['salary'] = v_salary
        if not v_salary:
            v_salary_min = None
            v_salary_max = None
            v_salary_currency = None
        else:
            v_salary = v_salary.getText().replace(u'\xa0', '')

            v_salary = re.split(r'\s|-', v_salary)

            if v_salary[0] == 'до':
                v_salary_min = None
                v_salary_max = int(v_salary[1])
            elif v_salary[0] == 'от':
                v_salary_min = int(v_salary[1])
                v_salary_max = None
            elif v_salary[0] == '-':
                v_salary_min = int(v_salary[0])
                v_salary_max = int(v_salary[1])
            else:
                v_salary_min = int(v_salary[0])
                v_salary_max = int(v_salary[1])

            v_salary_currency = v_salary[2]

        v_data['salary_min'] = v_salary_min
        v_data['salary_max'] = v_salary_max
        v_data['salary_currency'] = v_salary_currency

        all_vacancies.append(v_data)
    params['page'] += 1
    response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)

# pprint(all_vacancies)

df_hh = pd.DataFrame(all_vacancies)
df_hh.to_csv(f'hh.csv')
