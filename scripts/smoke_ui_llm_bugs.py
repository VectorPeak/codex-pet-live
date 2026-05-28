import json
import os
import sys
import tempfile
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_SMOKE_CONFIG_DIR = tempfile.TemporaryDirectory()
os.environ["CODEXPETLIVE_CONFIG_DIR"] = _SMOKE_CONFIG_DIR.name
os.environ.pop("PEAKDESKSPRITE_CONFIG_DIR", None)

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget

import CodexPetLive.settings as settings

settings.BASEDIR = ROOT
settings.basedir = ROOT
settings.init()

import CodexPetLive.Notification as notification_module
from CodexPetLive.Notification import SpriteNote
from CodexPetLive.SpriteSettings.LLMProviderUI import sanitize_provider_error
from CodexPetLive.bubbleManager import BubbleManager
from CodexPetLive.llm_client import LLMConfigError, LLMRequestError


def require(condition, message):
    if not condition:
        raise AssertionError(message)


class FakeBubbleText(QObject):
    closed_bubble = Signal(str)
    register_note = Signal(str, str)

    def __init__(self, note_index, *_args, **_kwargs):
        super().__init__()
        self.note_index = note_index
        self.height_margin = 0

    def height(self):
        return 10

    def startShow(self, height_margin):
        self.height_margin = height_margin

    def move_to_main(self, *_args):
        pass

    def _closeit(self):
        self.closed_bubble.emit(self.note_index)


class TestSpriteNote(SpriteNote):
    def __init__(self):
        QWidget.__init__(self)
        self.bubble_in_prepare = False
        self.note_in_prepare = False
        self.note_dict = {}
        self.height_dict = {}
        self.type_dict = {}
        self.bubble_dict = {}
        self.bb_height_dict = {}
        self.exist_bubble_types = {}
        self.icon_dict = {"system": {"image": QPixmap(1, 1)}}
        self._note_queue = deque()
        self._note_queue_timer = QTimer(self)
        self._note_queue_timer.setSingleShot(True)
        self._note_queue_timer.timeout.connect(self._process_next_notification)
        self._bubble_queue = deque()
        self._bubble_queue_timer = QTimer(self)
        self._bubble_queue_timer.setSingleShot(True)
        self._bubble_queue_timer.timeout.connect(self._process_next_bubble)

    def play_audio(self, *_args):
        pass


def test_notification_queue_releases_flag():
    QApplication.instance() or QApplication([])
    note = TestSpriteNote()
    logs = []
    note.noteToLog.connect(lambda _icon, message: logs.append(message))

    note.setup_notification("system", "notice")
    require(len(note._note_queue) == 1, "notification should be queued")
    note._process_next_notification()
    require(note.note_in_prepare is False, "notification flag should be released")
    require(logs == ["notice"], "notification should still write dashboard log")


def test_bubble_queue_releases_flag_and_respects_log_false():
    app = QApplication.instance() or QApplication([])
    original_bubble_text = notification_module.BubbleText
    notification_module.BubbleText = FakeBubbleText
    note = TestSpriteNote()
    logs = []
    note.noteToLog.connect(lambda _icon, message: logs.append(message))

    try:
        note.setup_bubbleText({"message": "hidden", "log": False}, 100, 100)
        note._process_next_bubble()
        require(note.bubble_in_prepare is False, "bubble flag should be released")
        require(logs == [], "log=False bubble should not be written to dashboard log")

        note.setup_bubbleText({"message": "visible", "log": True, "icon": "system"}, 100, 100)
        note._process_next_bubble()
        require(logs == ["visible"], "log=True bubble should be written to dashboard log")
        note._close_all_bubbles()
        app.processEvents()
    finally:
        notification_module.BubbleText = original_bubble_text


def test_bubble_config_utf8_sig_and_pet_fallback():
    manager = BubbleManager()
    with tempfile.TemporaryDirectory() as tmpdir:
        valid_path = os.path.join(tmpdir, "bubble_conf.json")
        with open(valid_path, "w", encoding="utf-8-sig") as f:
            json.dump({"pat_random_1": {"message": "你好"}}, f, ensure_ascii=False)
        loaded = manager._read_bubble_conf(valid_path)
        require(loaded["pat_random_1"]["message"] == "你好", "utf-8-sig bubble config should load")

        broken_path = os.path.join(tmpdir, "broken_bubble_conf.json")
        with open(broken_path, "w", encoding="utf-8") as f:
            f.write("{")
        loaded = manager._read_bubble_conf(broken_path, fallback={"fallback": True})
        require(loaded == {"fallback": True}, "broken pet bubble config should fall back")

    merged = manager._merge_pet_bubble_conf(
        {"hp_low": {"message": "base", "icon": "system"}},
        {"hp_low": {"message": "pet"}, "broken": "bad"},
    )
    require(merged["hp_low"]["message"] == "pet", "valid pet bubble override should apply")
    require("broken" not in merged, "invalid pet bubble entries should be ignored")


def test_provider_error_sanitizer():
    config_message = sanitize_provider_error(LLMConfigError("secret base_url model api key"))
    request_message = sanitize_provider_error(LLMRequestError("provider raw body with secrets"))
    require("secret" not in config_message.lower(), "config error should not expose raw details")
    require("secret" not in request_message.lower(), "request error should not expose raw details")
    require("隐藏敏感" in request_message, "request error should use sanitized provider failure text")


def main():
    test_notification_queue_releases_flag()
    test_bubble_queue_releases_flag_and_respects_log_false()
    test_bubble_config_utf8_sig_and_pet_fallback()
    test_provider_error_sanitizer()
    print("SMOKE_UI_LLM_BUGS_OK")


if __name__ == "__main__":
    sys.exit(main())
