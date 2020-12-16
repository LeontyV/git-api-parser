from config import USER, PASS, TOKEN
import requests

headers = {"Authorization": f"token {TOKEN}"}

branch = 'master'
page = 1
statuses = ['open', 'closed']
result_status = {}
for status in statuses:
    params = {
                    "Accept": "application/vnd.github.v3+json",
                    "q": f"repo:ytdl-org/youtube-dl is:pr is:{status} created:2020-06-01..2020-12-15",
                    "page": f"{page}",
                    "per_page": "100",
                    "sort": "created",
                    "base": branch,
                    "order": "desc",
                }
    query_url = f'https://api.github.com/search/issues'
    pr_content = requests.get(query_url, params=params, headers=headers)
    if pr_content.status_code == 200:
        result_status[status] = pr_content.json().get('total_count')

print(result_status)
