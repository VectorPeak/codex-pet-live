import os
import sys
from pathlib import Path


RESOURCE_DIR_ENV = "CODEXPETLIVE_RESOURCE_DIR"
LEGACY_RESOURCE_DIR_ENV = "PEAKDESKSPRITE_RESOURCE_DIR"


def _absolute_path(path):
    return Path(path).expanduser().resolve()


def _has_resource_layout(root):
    return (root / "res").is_dir()


def _candidate_roots():
    override = os.environ.get(RESOURCE_DIR_ENV, os.environ.get(LEGACY_RESOURCE_DIR_ENV))
    if override:
        yield Path(override)

    if getattr(sys, "frozen", False):
        executable = getattr(sys, "executable", None)
        if executable:
            yield Path(executable).resolve().parent

        bundle_dir = getattr(sys, "_MEIPASS", None)
        if bundle_dir:
            yield Path(bundle_dir)

    package_dir = Path(__file__).resolve().parent
    yield package_dir.parent

    try:
        yield Path.cwd()
    except OSError:
        pass


def resource_root():
    for candidate in _candidate_roots():
        root = _absolute_path(candidate)
        if _has_resource_layout(root):
            return str(root)

    return str(Path(__file__).resolve().parent.parent)


def executable_root():
    if getattr(sys, "frozen", False) and getattr(sys, "executable", None):
        return str(Path(sys.executable).resolve().parent)
    return resource_root()


def package_root():
    root = Path(resource_root()) / "CodexPetLive"
    if root.is_dir():
        return str(root)
    return str(Path(__file__).resolve().parent)


def resource_path(*parts):
    return os.path.join(resource_root(), *parts)


def package_path(*parts):
    return os.path.join(package_root(), *parts)


def set_runtime_cwd():
    root = resource_root()
    if os.path.abspath(os.getcwd()) != os.path.abspath(root):
        os.chdir(root)
    return root
