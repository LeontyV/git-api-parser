from config import TOKENS
import requests
from datetime import datetime as dt
from datetime import timedelta as d
import re

# token = TOKENS[0]
# headers = {"Authorization": f"token {token}"}
# params = {"Accept": "application/vnd.github.v3+json"}
# # print(headers)
# api_url = 'https://api.github.com/rate_limit'
# content = requests.get(api_url, params=params, headers=headers)
# print(content)
# print(content.content)

#
# branch = 'master'
# page = 1
# statuses = ['open', 'closed']
# result_status = {}
# for status in statuses:
#     params = {
#                     "Accept": "application/vnd.github.v3+json",
#                     "q": f"repo:ytdl-org/youtube-dl is:pr is:{status} created:2020-06-01..2020-12-15",
#                     "page": f"{page}",
#                     "per_page": "100",
#                     "sort": "created",
#                     "base": branch,
#                     "order": "desc",
#                 }
#     query_url = f'https://api.github.com/search/issues'
#     pr_content = requests.get(query_url, params=params, headers=headers)
#     if pr_content.status_code == 200:
#         result_status[status] = pr_content.json().get('total_count')
#
# print(result_status)

example = 'https://github.com/ytdl-orG/youtube-dl'
pattern = r"(https://github.com/[\w-]+/[\w-]+)"
match = re.match(pattern, example)
print(match)