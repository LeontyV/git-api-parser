import sys

from api import GetFromGitApi
from config import TOKEN

if __name__ == '__main__':
    git = GetFromGitApi(token=TOKEN)
    # git.get_top_authors(sys.argv)
    git.get_pull_requests(sys.argv)

    # python main.py -url https://github.com/ytdl-org/youtube-dl -since 2020-12-12T00:00:00Z -until 2020-12-15T00:00:00Z

