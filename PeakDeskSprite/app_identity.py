import os


DEFAULT_APP_NAME = "PeakDeskSprite"
DEFAULT_ENV_PREFIX = "PEAKDESKSPRITE"
DEFAULT_PROJECT_REPOSITORY = "VectorPeak/PeakDeskSprite"


def _env_name(key, prefix=None):
    return f"{prefix or ENV_PREFIX}_{key}"


ENV_PREFIX = os.environ.get(f"{DEFAULT_ENV_PREFIX}_ENV_PREFIX", DEFAULT_ENV_PREFIX)
APP_NAME = os.environ.get(_env_name("APP_NAME"), DEFAULT_APP_NAME)
CONFIG_APP_NAME = os.environ.get(_env_name("CONFIG_APP_NAME"), APP_NAME)
DOCUMENTS_DIR_NAME = os.environ.get(_env_name("DOCUMENTS_DIR_NAME"), APP_NAME)
CONFIG_DIR_ENV = _env_name("CONFIG_DIR")
LLM_API_KEY_ENV = _env_name("LLM_API_KEY")

PROJECT_REPOSITORY = os.environ.get(_env_name("PROJECT_REPOSITORY"), DEFAULT_PROJECT_REPOSITORY)
PROJECT_URL = os.environ.get(_env_name("PROJECT_URL"), f"https://github.com/{PROJECT_REPOSITORY}")
HELP_URL = os.environ.get(_env_name("HELP_URL"), f"{PROJECT_URL}/issues")
DEVDOC_URL = os.environ.get(_env_name("DEVDOC_URL"), f"{PROJECT_URL}/blob/main/docs/art_dev.md")
CHARCOLLECT_LINK = os.environ.get(_env_name("CHARCOLLECT_LINK"), f"{PROJECT_URL}/blob/main/docs/collection.md")
ITEMCOLLECT_LINK = os.environ.get(_env_name("ITEMCOLLECT_LINK"), f"{PROJECT_URL}/blob/main/docs/collection.md")
PETCOLLECT_LINK = os.environ.get(_env_name("PETCOLLECT_LINK"), f"{PROJECT_URL}/blob/main/docs/collection.md")
RELEASE_API = os.environ.get(_env_name("RELEASE_API"), f"https://api.github.com/repos/{PROJECT_REPOSITORY}/releases/latest")
RELEASE_URL = os.environ.get(_env_name("RELEASE_URL"), f"{PROJECT_URL}/releases/latest")
