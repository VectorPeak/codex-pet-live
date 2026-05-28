import os
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main():
    from CodexPetLive.resource_paths import resource_path, resource_root

    expected_root = str(REPO_ROOT)
    actual_root = resource_root()
    if os.path.normcase(os.path.normpath(actual_root)) != os.path.normcase(os.path.normpath(expected_root)):
        raise AssertionError(f"unexpected resource root: {actual_root}")

    language_path = resource_path("res", "language", "language.json")
    if not os.path.isfile(language_path):
        raise AssertionError(f"missing language resource: {language_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            before_import_cwd = os.getcwd()
            import CodexPetLive.__main__ as app_entry

            if os.getcwd() != before_import_cwd:
                raise AssertionError("importing CodexPetLive.__main__ changed cwd")

            import PeakDeskSprite.__main__ as compat_entry
            from PeakDeskSprite.PeakDeskSprite import PetWidget as _CompatPetWidget
            from CodexPetLive.CodexPetLive import PetWidget

            if compat_entry.main is not app_entry.main:
                raise AssertionError("compatibility entry point does not forward to CodexPetLive")
            if _CompatPetWidget is not PetWidget:
                raise AssertionError("compatibility PetWidget does not forward to CodexPetLive")

            settings_root = app_entry.settings.BASEDIR
            if os.path.normcase(os.path.normpath(settings_root)) != os.path.normcase(os.path.normpath(expected_root)):
                raise AssertionError(f"unexpected settings.BASEDIR: {settings_root}")
        finally:
            os.chdir(original_cwd)

    print("RESOURCE_PATHS_OK")


if __name__ == "__main__":
    main()
