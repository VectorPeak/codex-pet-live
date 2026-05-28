import os


DEFAULT_APP_NAME = "CodexPetLive"
DEFAULT_ENV_PREFIX = "CODEXPETLIVE"
LEGACY_ENV_PREFIX = "PEAKDESKSPRITE"
DEFAULT_PROJECT_REPOSITORY = "VectorPeak/CodexPetLive"


def _env_name(key, prefix=None):
    return f"{prefix or ENV_PREFIX}_{key}"


def _env_value(key, default, prefix=None):
    new_name = f"{prefix or ENV_PREFIX}_{key}"
    legacy_name = f"{LEGACY_ENV_PREFIX}_{key}"
    return os.environ.get(new_name, os.environ.get(legacy_name, default))


ENV_PREFIX = os.environ.get(
    f"{DEFAULT_ENV_PREFIX}_ENV_PREFIX",
    os.environ.get(f"{LEGACY_ENV_PREFIX}_ENV_PREFIX", DEFAULT_ENV_PREFIX),
)
APP_NAME = _env_value("APP_NAME", DEFAULT_APP_NAME)
CONFIG_APP_NAME = _env_value("CONFIG_APP_NAME", APP_NAME)
DOCUMENTS_DIR_NAME = _env_value("DOCUMENTS_DIR_NAME", APP_NAME)
CONFIG_DIR_ENV = _env_name("CONFIG_DIR")
LLM_API_KEY_ENV = _env_name("LLM_API_KEY")
LEGACY_CONFIG_DIR_ENV = f"{LEGACY_ENV_PREFIX}_CONFIG_DIR"
LEGACY_LLM_API_KEY_ENV = f"{LEGACY_ENV_PREFIX}_LLM_API_KEY"

PROJECT_REPOSITORY = _env_value("PROJECT_REPOSITORY", DEFAULT_PROJECT_REPOSITORY)
PROJECT_URL = _env_value("PROJECT_URL", f"https://github.com/{PROJECT_REPOSITORY}")
HELP_URL = _env_value("HELP_URL", f"{PROJECT_URL}/issues")
DEVDOC_URL = _env_value("DEVDOC_URL", f"{PROJECT_URL}/blob/main/docs/art_dev.md")
CHARCOLLECT_LINK = _env_value("CHARCOLLECT_LINK", f"{PROJECT_URL}/releases")
ITEMCOLLECT_LINK = _env_value("ITEMCOLLECT_LINK", f"{PROJECT_URL}/releases")
PETCOLLECT_LINK = _env_value("PETCOLLECT_LINK", f"{PROJECT_URL}/releases")
RELEASE_API = _env_value("RELEASE_API", f"https://api.github.com/repos/{PROJECT_REPOSITORY}/releases/latest")
RELEASE_URL = _env_value("RELEASE_URL", f"{PROJECT_URL}/releases/latest")
