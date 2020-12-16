import requests

import json
from collections import Counter
from datetime import datetime as dt
from datetime import timedelta as d


class GetFromGitApi(object):
    """
    Нужно постараться сделать максимально надежный, отказоустойчивый скрипт, в том
    числе с учетом ограничений API на кол-во запросов
    Допустим, что данный скрипт необходимо выполнять регулярно. В пояснительной
    записке предложите вариант реализации CI/CD для подобного сервиса.

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
    def print_pr(result_dict, querry):
        cols_names = list(result_dict.keys())
        cols_values = list(result_dict.values())
        length_name = max(len(elem) for elem in cols_names)
        length_value = max(len(str(elem)) for elem in cols_values)
        gutter = 2
        length_name += gutter
        length_value += gutter
        width = length_name + length_value
        if len(querry) > width + 9:
            width = len(querry)
        print(' '*((width + 9 - len(querry))//2) + f' {querry}')
        print('-' * (width + 9))
        print(f'| {cols_names[0] + " " * (length_name - len(cols_names[0]))}' +
              f'| {cols_names[1] + " " * (length_value - len(cols_names[1]) + 4)}|')
        print('|' + '-' * (width + 7) + '|')
        print(f'| {str(cols_values[0]) + " " * (length_name - len(str(cols_values[0])))}' +
              f'| {str(cols_values[1]) + " " * (length_value - len(str(cols_values[1])) + 4)}|')
        print('-' * (width + 9))

    @staticmethod
    def print_old_pr(result_dict, querry):
        cols_names = list(result_dict.keys())
        cols_names.extend(list(result_dict.values()))
        width = max(len(str(elem)) for elem in cols_names)
        gutter = 2
        width += gutter
        if len(querry) > width + gutter:
            width = len(querry)
        print(' ' * ((width + gutter - len(querry)) // 2) + f' {querry}')
        print('-' * (width+gutter))
        print(f'| {cols_names[0] + " " * (width - len(cols_names[0]) - 1)}|')
        print('|' + '-' * (width) + '|')
        print(f'| {str(cols_names[1]) + " " * (width - len(str(cols_names[1])) - 1)}|')
        print('-' * (width+gutter))

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
        querry = 'pull requests'
        self.print_pr(result_status, querry)

    def get_older_pull_requests(self, params):
        """"
        Количество “старых” pull requests на заданном периоде времени по дате создания
        PR и заданной ветке, являющейся базовой для этого PR. Pull request считается
        старым, если он не закрывается в течение 30 дней и до сих пор открыт.
        """
        self.get_params(params)
        owner = self.url.split('/')[-2]
        repo = self.url.split('/')[-1]

        curr_dt = dt.now()

        old_dt_obj = dt.strptime(self.since, '%Y-%m-%dT%H:%M:%SZ')
        delta_dt = curr_dt - old_dt_obj
        delta_30d = d(days=30)
        if delta_dt.days >= 30:
            self.until = dt.strftime(dt.strptime(self.until, '%Y-%m-%dT%H:%M:%SZ') - delta_30d, '%Y-%m-%dT%H:%M:%SZ')
        page = 1
        status = 'open'
        result_status = {}
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
        older_pr_content = requests.get(query_url, params=params, headers=self.headers)
        if older_pr_content.status_code == 200:
            result_status['old_pr'] = older_pr_content.json().get('total_count')

        querry = 'old pull requests'
        self.print_old_pr(result_status, querry)

    def get_issues(self, params):
        """
        Количество открытых и закрытых issues на заданном периоде времени по дате
        создания issue
        """
        self.get_params(params)
        owner = self.url.split('/')[-2]
        repo = self.url.split('/')[-1]

        page = 1
        statuses = ['open', 'closed']
        result_status = {}
        for status in statuses:
            params = {
                "Accept": "application/vnd.github.v3+json",
                "q": f"repo:{owner}/{repo} is:issue is:{status} created:{self.since[:10]}..{self.until[:10]}",
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

        querry = 'issues'
        self.print_pr(result_status, querry)

    def get_old_issues(self, params):
        """
        Количество “старых” issues на заданном периоде времени по дате создания issue.
        Issue считается старым, если он не закрывается в течение 14 дней.
        """
        self.get_params(params)
        owner = self.url.split('/')[-2]
        repo = self.url.split('/')[-1]

        curr_dt = dt.now()

        old_dt_obj = dt.strptime(self.since, '%Y-%m-%dT%H:%M:%SZ')
        delta_dt = curr_dt - old_dt_obj
        delta_30d = d(days=14)
        if delta_dt.days >= 14:
            self.until = dt.strftime(dt.strptime(self.until, '%Y-%m-%dT%H:%M:%SZ') - delta_30d, '%Y-%m-%dT%H:%M:%SZ')
        page = 1
        status = 'open'
        result_status = {}
        params = {
            "Accept": "application/vnd.github.v3+json",
            "q": f"repo:{owner}/{repo} is:issue is:{status} created:{self.since[:10]}..{self.until[:10]}",
            "page": f"{page}",
            "per_page": "100",
            "sort": "created",
            "base": self.branch,
            "order": "desc",
        }
        query_url = f'https://api.github.com/search/issues'
        older_pr_content = requests.get(query_url, params=params, headers=self.headers)
        if older_pr_content.status_code == 200:
            result_status['old_issues'] = older_pr_content.json().get('total_count')

        querry = 'old issues'
        self.print_old_pr(result_status, querry)