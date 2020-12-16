import os

from dotenv import load_dotenv

load_dotenv()

USER = str(os.getenv("GIT_USER"))
PASS = str(os.getenv("GIT_PASS"))
TOKEN = str(os.getenv("TOKEN"))