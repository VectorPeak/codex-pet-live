import os
from sys import platform

from CodexPetLive import app_identity


def app_config_dir(app_name=None, env_var=None):
    config_app_name = app_name or app_identity.CONFIG_APP_NAME
    if env_var:
        override = os.environ.get(env_var)
    else:
        override = os.environ.get(
            app_identity.CONFIG_DIR_ENV,
            os.environ.get(app_identity.LEGACY_CONFIG_DIR_ENV),
        )
    if override:
        return os.path.abspath(os.path.expanduser(override))

    if platform == "win32":
        root = (
            os.environ.get("APPDATA")
            or os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "AppData", "Roaming")
        )
        return os.path.join(root, config_app_name)

    if platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", config_app_name)

    return os.path.join(os.path.expanduser("~"), ".config", config_app_name)


def runtime_data_dir(config_dir=None):
    return os.path.join(config_dir or app_config_dir(), "data")


def documents_app_dir(*parts, app_name=None):
    return os.path.join(app_name or app_identity.DOCUMENTS_DIR_NAME, *parts)
