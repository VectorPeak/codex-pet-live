# coding:utf-8
import os

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
)

from qfluentwidgets import (
    CaptionLabel, FluentIcon as FIF, InfoBar, InfoBarPosition,
    PrimaryPushButton, PushButton, SubtitleLabel, TransparentToolButton,
)

import PeakDeskSprite.settings as settings
from PeakDeskSprite import llm_chat_store
from PeakDeskSprite.llm_client import (
    build_chat_messages,
    request_chat_completion,
    stream_chat_completion,
    validate_config,
)


basedir = settings.BASEDIR


class ChatInputEdit(QPlainTextEdit):
    sendRequested = Signal(name="sendRequested")

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not event.modifiers() & Qt.ShiftModifier:
            self.sendRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class LLMChatThread(QThread):
    chunk = Signal(str, name="chunk")
    done = Signal(bool, str, name="done")

    def __init__(self, config, user_message, history, role_prompt, pet_name, usertag, language_code, parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.user_message = user_message
        self.history = list(history or [])
        self.role_prompt = role_prompt
        self.pet_name = pet_name
        self.usertag = usertag
        self.language_code = language_code

    def run(self):
        try:
            messages = build_chat_messages(
                self.config,
                self.user_message,
                history=self.history,
                pet_name=self.pet_name,
                usertag=self.usertag,
                language_code=self.language_code,
                role_prompt=self.role_prompt,
            )
            max_reply_chars = int(self.config.get("max_chat_reply_chars", 4000))
            max_tokens = int(self.config.get("chat_max_tokens", 800))
            if self.config.get("chat_stream_enabled", True):
                chunks = []
                for chunk in stream_chat_completion(
                    self.config,
                    messages,
                    max_reply_chars=max_reply_chars,
                    max_tokens=max_tokens,
                ):
                    chunks.append(chunk)
                    self.chunk.emit(chunk)
                reply = "".join(chunks)
            else:
                reply = request_chat_completion(
                    self.config,
                    messages,
                    max_reply_chars=max_reply_chars,
                    compact=False,
                    max_tokens=max_tokens,
                )
            self.done.emit(True, reply)
        except Exception as exc:
            self.done.emit(False, str(exc))


class RolePromptDialog(QDialog):
    def __init__(self, pet_name, current_prompt, parent=None):
        super().__init__(parent)
        self.pet_name = pet_name or "PeakDeskSprite"
        self.setWindowTitle(self.tr("编辑人设提示词"))
        self.setModal(True)
        self.resize(620, 480)

        self.titleLabel = SubtitleLabel(self.tr(f"编辑人设提示词 - {self.pet_name}"), self)
        self.descLabel = CaptionLabel(
            self.tr("自定义桌宠的说话方式和行为。留空或点击“恢复默认”将使用内置人设。"),
            self,
        )
        self.editor = QPlainTextEdit(self)
        self.editor.setPlainText(current_prompt or llm_chat_store.default_role_prompt(self.pet_name))
        self.editor.setMinimumHeight(260)
        self.counterLabel = CaptionLabel("", self)
        self.restoreButton = PushButton(self.tr("恢复默认"), self)
        self.saveButton = PrimaryPushButton(self.tr("保存"), self)
        self.cancelButton = PushButton(self.tr("取消"), self)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.restoreButton, 0, Qt.AlignLeft)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.cancelButton)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.descLabel)
        layout.addWidget(self.editor, 1)
        layout.addWidget(self.counterLabel)
        layout.addLayout(buttonLayout)

        self.editor.textChanged.connect(self._update_counter)
        self.restoreButton.clicked.connect(self._restore_default)
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self._update_counter()
        self.setStyleSheet("""
            QPlainTextEdit {
                border: 1px solid #d8dde6;
                border-radius: 6px;
                padding: 10px;
                background: #ffffff;
                color: #1f2328;
                font-size: 14px;
            }
        """)

    def _restore_default(self):
        self.editor.setPlainText(llm_chat_store.default_role_prompt(self.pet_name))

    def _update_counter(self):
        self.counterLabel.setText(f"{len(self.editor.toPlainText())} / 2000")

    def prompt(self):
        return self.editor.toPlainText().strip() or llm_chat_store.default_role_prompt(self.pet_name)


class MessageBubble(QWidget):
    def __init__(self, role, content, avatar_path=None, parent=None):
        super().__init__(parent)
        self.role = role
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 8, 18, 8)
        layout.setSpacing(10)

        self.bubbleLabel = QLabel(content, self)
        self.bubbleLabel.setWordWrap(True)
        self.bubbleLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.bubbleLabel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.bubbleLabel.setMaximumWidth(520)

        if role == "user":
            self.bubbleLabel.setObjectName("userBubble")
            layout.addItem(QSpacerItem(40, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
            layout.addWidget(self.bubbleLabel, 0, Qt.AlignRight | Qt.AlignTop)
        else:
            avatar = QLabel(self)
            avatar.setFixedSize(34, 34)
            avatar.setScaledContents(True)
            pixmap = QPixmap(avatar_path) if avatar_path and os.path.exists(avatar_path) else QPixmap()
            if pixmap.isNull():
                pixmap = QPixmap(os.path.join(basedir, "res/icons/SystemPanel.png"))
            avatar.setPixmap(pixmap.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.bubbleLabel.setObjectName("assistantBubble")
            layout.addWidget(avatar, 0, Qt.AlignLeft | Qt.AlignTop)
            layout.addWidget(self.bubbleLabel, 0, Qt.AlignLeft | Qt.AlignTop)
            layout.addItem(QSpacerItem(40, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def set_content(self, content):
        self.bubbleLabel.setText(content)

    def append_content(self, content):
        self.bubbleLabel.setText(self.bubbleLabel.text() + content)

    def content(self):
        return self.bubbleLabel.text()


class LLMChatInterface(QWidget):
    openProviderSettings = Signal(name="openProviderSettings")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LLMChatInterface")
        self.chatThread = None
        self.pendingBubble = None
        self.streamingReply = ""
        self.chatData = llm_chat_store.load_chat_data()

        self.titleLabel = QLabel(self.tr("聊天"), self)
        self.titleLabel.setObjectName("settingLabel")

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setObjectName("chatScrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.viewport().setObjectName("chatViewport")
        self.messageWidget = QWidget()
        self.messageWidget.setObjectName("messageWidget")
        self.messageLayout = QVBoxLayout(self.messageWidget)
        self.messageLayout.setContentsMargins(12, 12, 12, 12)
        self.messageLayout.setSpacing(2)
        self.messageLayout.addStretch(1)
        self.scrollArea.setWidget(self.messageWidget)

        self.inputFrame = QFrame(self)
        self.inputFrame.setObjectName("inputFrame")
        self.roleButton = PushButton(FIF.EDIT, self.tr("角色设定"), self.inputFrame)
        self.saveButton = TransparentToolButton(FIF.SAVE, self.inputFrame)
        self.saveButton.setToolTip(self.tr("保存当前聊天记录"))
        self.providerButton = TransparentToolButton(FIF.SETTING, self.inputFrame)
        self.providerButton.setToolTip(self.tr("打开大模型服务设置"))
        self.inputEdit = ChatInputEdit(self.inputFrame)
        self.inputEdit.setPlaceholderText(self.tr("输入消息...（Enter 发送，Shift+Enter 换行）"))
        self.inputEdit.setFixedHeight(108)
        self.disclaimerLabel = CaptionLabel(self.tr("内容由 AI 生成，请仔细甄别"), self.inputFrame)
        self.sendButton = PrimaryPushButton(self.tr("发送"), self.inputFrame)

        toolbar = QHBoxLayout()
        toolbar.addWidget(self.roleButton, 0, Qt.AlignLeft)
        toolbar.addStretch(1)
        toolbar.addWidget(self.saveButton, 0, Qt.AlignRight)
        toolbar.addWidget(self.providerButton, 0, Qt.AlignRight)

        bottom = QHBoxLayout()
        bottom.addWidget(self.disclaimerLabel, 1, Qt.AlignCenter)
        bottom.addWidget(self.sendButton, 0, Qt.AlignRight)

        inputLayout = QVBoxLayout(self.inputFrame)
        inputLayout.setContentsMargins(16, 12, 16, 10)
        inputLayout.setSpacing(8)
        inputLayout.addLayout(toolbar)
        inputLayout.addWidget(self.inputEdit)
        inputLayout.addLayout(bottom)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 72, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.scrollArea, 1)
        layout.addWidget(self.inputFrame, 0)

        self.roleButton.clicked.connect(self._edit_role_prompt)
        self.saveButton.clicked.connect(self._save_history)
        self.providerButton.clicked.connect(self.openProviderSettings.emit)
        self.sendButton.clicked.connect(self._send_message)
        self.inputEdit.sendRequested.connect(self._send_message)

        self._render_history()
        self._set_qss()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.titleLabel.move(50, 24)

    def _set_qss(self):
        self.setStyleSheet("""
            #LLMChatInterface {
                background: #f5f7fb;
            }
            #inputFrame {
                background: #ffffff;
                border-top: 1px solid #dce2ea;
            }
            QScrollArea#chatScrollArea {
                background: #f5f7fb;
                border: none;
            }
            QWidget#chatViewport {
                background: #f5f7fb;
            }
            QWidget#messageWidget {
                background: #f5f7fb;
            }
            QPlainTextEdit {
                border: 0;
                border-bottom: 3px solid #009faa;
                background: #ffffff;
                color: #1f2328;
                padding: 8px 4px;
                font-size: 14px;
            }
            QLabel#assistantBubble {
                background: #ffffff;
                color: #1f2328;
                border-radius: 8px;
                padding: 10px 12px;
            }
            QLabel#userBubble {
                background: #087bdc;
                color: #ffffff;
                border-radius: 8px;
                padding: 10px 12px;
            }
            QLabel#settingLabel {
                color: #1f2328;
                font-size: 20px;
                font-weight: 600;
            }
        """)

    def _current_pet_name(self):
        return getattr(settings, "petname", "") or getattr(settings, "default_pet", "") or "PeakDeskSprite"

    def _current_avatar_path(self):
        pet_name = self._current_pet_name()
        info_path = os.path.join(basedir, "res", "role", pet_name, "info", "pfp.png")
        if os.path.exists(info_path):
            return info_path
        return os.path.join(basedir, "res", "icons", "SystemPanel.png")

    def _insert_message_widget(self, role, content):
        index = max(0, self.messageLayout.count() - 1)
        widget = MessageBubble(role, content, self._current_avatar_path(), self.messageWidget)
        self.messageLayout.insertWidget(index, widget)
        self._scroll_to_bottom()
        return widget

    def _scroll_to_bottom(self):
        bar = self.scrollArea.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _render_history(self):
        while self.messageLayout.count() > 1:
            item = self.messageLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.chatData.get("messages"):
            pet_name = self._current_pet_name()
            self._insert_message_widget("assistant", self.tr(f"你好，我是 {pet_name}。想聊什么都可以。"))
            return

        for message in self.chatData.get("messages", []):
            self._insert_message_widget(message["role"], message["content"])

    def _history_for_request(self):
        return list(self.chatData.get("messages", []))[-16:]

    def _set_sending(self, sending):
        self.sendButton.setEnabled(not sending)
        self.inputEdit.setEnabled(not sending)
        self.sendButton.setText(self.tr("发送中...") if sending else self.tr("发送"))

    def _show_warning(self, title, content):
        InfoBar.warning(
            title,
            content,
            duration=5000,
            position=InfoBarPosition.BOTTOM,
            parent=self.window(),
        )

    def _send_message(self):
        if self.chatThread and self.chatThread.isRunning():
            return

        user_message = self.inputEdit.toPlainText().strip()
        if not user_message:
            return

        config = settings.llm_provider_config.copy()
        if not config.get("enabled", False):
            self._show_warning(self.tr("大模型服务未启用"), self.tr("请先在“大模型服务”页面启用并完成配置。"))
            return
        try:
            validate_config(config)
        except Exception:
            self._show_warning(self.tr("大模型服务未就绪"), self.tr("请先在“大模型服务”页面完成接口、模型和密钥配置。"))
            return

        history = self._history_for_request()
        pet_name = self._current_pet_name()
        role_prompt = llm_chat_store.get_role_prompt(self.chatData, pet_name)

        self.inputEdit.clear()
        self._insert_message_widget("user", user_message)
        llm_chat_store.append_message(self.chatData, "user", user_message)
        self.streamingReply = ""
        self.pendingBubble = self._insert_message_widget("assistant", self.tr("正在思考..."))
        self._set_sending(True)

        usertag = settings.usertag_dict.get(pet_name, "")
        self.chatThread = LLMChatThread(
            config,
            user_message=user_message,
            history=history,
            role_prompt=role_prompt,
            pet_name=pet_name,
            usertag=usertag,
            language_code=settings.language_code,
            parent=self,
        )
        self.chatThread.chunk.connect(self._reply_chunk)
        self.chatThread.done.connect(self._reply_done)
        self.chatThread.finished.connect(self.chatThread.deleteLater)
        self.chatThread.start()

    def _reply_chunk(self, chunk):
        if not self.pendingBubble:
            return
        if not self.streamingReply:
            self.pendingBubble.set_content("")
        self.streamingReply += chunk
        self.pendingBubble.set_content(self.streamingReply)
        self._scroll_to_bottom()

    def _reply_done(self, ok, message):
        self._set_sending(False)
        if self.pendingBubble and not ok:
            self.messageLayout.removeWidget(self.pendingBubble)
            self.pendingBubble.deleteLater()
            self.pendingBubble = None

        if ok:
            reply = (message or self.streamingReply).strip()
            if self.pendingBubble:
                self.pendingBubble.set_content(reply)
            else:
                self._insert_message_widget("assistant", reply)
            llm_chat_store.append_message(self.chatData, "assistant", reply)
            self.pendingBubble = None
            self.streamingReply = ""
        else:
            self._insert_message_widget("assistant", self.tr("这次没有成功连上大模型服务，请检查配置后再试。"))
            self._show_warning(self.tr("发送失败"), self.tr("服务商请求失败，已隐藏敏感连接信息。"))

        self.chatThread = None

    def _edit_role_prompt(self):
        pet_name = self._current_pet_name()
        dialog = RolePromptDialog(
            pet_name,
            llm_chat_store.get_role_prompt(self.chatData, pet_name),
            self.window(),
        )
        if dialog.exec() == QDialog.Accepted:
            llm_chat_store.set_role_prompt(self.chatData, pet_name, dialog.prompt())
            InfoBar.success(
                "",
                self.tr("角色设定已保存"),
                duration=2200,
                position=InfoBarPosition.BOTTOM,
                parent=self.window(),
            )

    def _save_history(self):
        llm_chat_store.save_chat_data(self.chatData)
        InfoBar.success(
            "",
            self.tr("聊天记录已保存"),
            duration=1800,
            position=InfoBarPosition.BOTTOM,
            parent=self.window(),
        )
