from config import USER, PASS, TOKEN
import requests
from datetime import datetime as dt
from datetime import timedelta as d

# headers = {"Authorization": f"token {TOKEN}"}
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

old_dt = '2020-10-15T00:00:00Z'
curr_dt = dt.now()

old_dt_obj = dt.strptime(old_dt, '%Y-%m-%dT%H:%M:%SZ')
print(old_dt_obj)
delta_dt = curr_dt - old_dt_obj
print(delta_dt)
new_dt = old_dt_obj + delta_dt
print(new_dt - d(days=30))