import requests

import json
from collections import Counter
from datetime import datetime as dt


class GetFromGitApi(object):
    """
    URL публичного репозитория на github.com.
    Дата начала анализа. Если пустая, то неограничено.
    Дата окончания анализа. Если пустая, то неограничено.
    Ветка репозитория. По умолчанию - master.
    Параметры должны передаваться в скрипт через командную строку
    """

    def __init__(self, token=None, use_session=True):
        if use_session:
            self.request = requests.Session()
        self.api_url = 'https://api.github.com'

        self.url = ''
        self.since = ''
        self.until = ''
        self.branch = 'master'
        self.headers = {}
        if token is not None:
            self.headers.update({"Authorization": f"token {token}"})

    def get_params(self, params):
        if '-url' in params:
            index = params.index('-url')
            self.url = params[index + 1]
        if '-branch' in params:
            index = params.index('-branch')
            self.branch = params[index + 1]
        if '-since' in params:
            index = params.index('-since')
            self.since = params[index + 1]
        if '-until' in params:
            index = params.index('-until')
            self.until = params[index + 1]

    @staticmethod
    def print_best_authors(authors):
        length_name = max(len(author[0]) for author in authors)
        length_count = max(len(str(author[1])) for author in authors)
        name_cols = ['login', 'commits']
        if len(name_cols[0]) > length_count:
            length_count = len(name_cols[0])
        gutter = 2
        length_name = length_name + gutter
        length_count = length_count + gutter
        width = length_name + length_count

        print('-' * (width + 5))
        print(f'| {name_cols[0]     + " " * (length_name - len(name_cols[0]))}' +
              f'| {name_cols[1]     + " " * (length_count - len(name_cols[1]))}|')
        print('|' + '-' * (width + 3) + '|')
        for author in authors:
            print(f'| {author[0]        + " " * (length_name - len(author[0]))}' +
                  f'| {str(author[1])   + " " * (length_count - len(str(author[1])))}|')
        print('-' * (width + 5))

    @staticmethod
    def print_pr(pr):
        cols_names = list(pr.keys())
        cols_values = list(pr.values())
        length_name = max(len(elem) for elem in cols_names)
        length_value = max(len(str(elem)) for elem in cols_values)
        gutter = 2
        length_name += gutter
        length_value += gutter
        width = length_name + length_value
        print('-' * (width + 9))
        print(f'| {cols_names[0] + " " * (length_name - len(cols_names[0]))}' +
              f'| {cols_names[1] + " " * (length_value - len(cols_names[1]) + 4)}|')
        print('|' + '-' * (width + 7) + '|')
        print(f'| {str(cols_values[0]) + " " * (length_name - len(str(cols_values[0])))}' +
              f'| {str(cols_values[1]) + " " * (length_value - len(str(cols_values[1])) + 4)}|')
        print('-' * (width + 9))

    def get_top_authors(self, params):
        """
        Самые активные участники. Таблица из 2 столбцов: login автора, количество его
        коммитов. Таблица отсортирована по количеству коммитов по убыванию. Не
        более 30 строк. Анализ производится на заданном периоде времени и заданной
        ветке
        """
        self.get_params(params)
        owner = self.url.split('/')[-2]
        repo = self.url.split('/')[-1]

        commits = []
        page = 1
        while True:
            params = {
                "Accept": "application/vnd.github.v3+json",
                "page": f"{page}",
                "per_page": "100",
                "sort": "created",
                "branch": self.branch,
                "since": self.since,
                "until": self.until
            }
            query_url = f'https://api.github.com/repos/{owner}/{repo}/commits'
            commits_content = self.request.get(query_url, params=params, headers=self.headers)

            if not commits_content.json():
                break
            else:
                commits.extend(commits_content.json())
                page += 1

        authors = []

        for commit in commits:
            if commit.get('author') is not None:
                authors.append(commit.get('author').get('login'))

        count_authors = list(Counter(authors).most_common(30))

        self.print_best_authors(count_authors)

    def get_pull_requests(self, params):
        """
        Количество открытых и закрытых pull requests на заданном периоде времени по
        дате создания PR и заданной ветке, являющейся базовой для этого PR.
        """
        self.get_params(params)
        owner = self.url.split('/')[-2]
        repo = self.url.split('/')[-1]

        commits = []
        page = 1
        statuses = ['open', 'closed']
        result_status = {}
        for status in statuses:
            params = {
                "Accept": "application/vnd.github.v3+json",
                "q": f"repo:{owner}/{repo} is:pr is:{status} created:{self.since[:10]}..{self.until[:10]}",
                "page": f"{page}",
                "per_page": "100",
                "sort": "created",
                "base": self.branch,
                "order": "desc",
            }
            query_url = f'https://api.github.com/search/issues'
            pr_content = requests.get(query_url, params=params, headers=self.headers)
            if pr_content.status_code == 200:
                result_status[status] = pr_content.json().get('total_count')

        self.print_pr(result_status)