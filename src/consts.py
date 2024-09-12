"""Settings for the project."""
import os
from pathlib import Path
from dotenv import dotenv_values

PROJECT_PATH = Path(__file__).parent.parent
ENV_PATH = PROJECT_PATH / ".env"
config_env = dotenv_values(ENV_PATH)

YANDEX_API_KEY = os.environ.get(
    "YANDEX_API_KEY", config_env.get("YANDEX_API_KEY"))
YANDEX_FOLDER_ID = os.environ.get(
    "YANDEX_FOLDER_ID", config_env.get("YANDEX_FOLDER_ID"))
OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY", config_env.get("OPENAI_API_KEY"))
PROXY_URL = os.environ.get("PROXY_URL", config_env.get("PROXY_URL"))
TG_TOKEN = os.environ.get("TG_TOKEN", config_env.get("TG_TOKEN"))
SQLALCHEMY_URL = os.environ.get(
    "SQLALCHEMY_URL", config_env.get("SQLALCHEMY_URL"))
