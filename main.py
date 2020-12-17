import sys

from api import GetFromGitApi

if __name__ == '__main__':
    git = GetFromGitApi(use_session=True)
    git.get_top_authors(sys.argv)
    git.get_pull_requests(sys.argv)
    git.get_older_pull_requests(sys.argv)
    git.get_issues(sys.argv)
    git.get_old_issues(sys.argv)
    print(git.count_requests)

    # python main.py -url https://github.com/ytdl-org/youtube-dl -since 2020-12-12T00:00:00Z -until 2020-12-15T00:00:00Z

