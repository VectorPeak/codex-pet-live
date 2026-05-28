# coding:utf-8
import os

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel

from qfluentwidgets import (
    SettingCardGroup, SwitchSettingCard, ScrollArea, ExpandLayout,
    InfoBar, InfoBarPosition, FluentIcon as FIF,
)

import CodexPetLive.settings as settings
from CodexPetLive import app_identity
from CodexPetLive.llm_client import (
    LLMConfigError,
    PROVIDER_PRESETS,
    build_bubble_messages,
    load_secret_api_key,
    request_chat_completion,
    save_secret_api_key,
)
from .custom_utils import (
    SpriteComboBoxSettingCard,
    SpriteLineEditSettingCard,
    SpritePushButtonSettingCard,
    SpriteRangeSettingCard,
)

basedir = settings.BASEDIR


class LLMTestThread(QThread):
    done = Signal(bool, str, name="done")

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config.copy()

    def run(self):
        try:
            messages = build_bubble_messages(
                self.config,
                event_name="connection_test",
                fallback_message="Say hello from the desktop pet.",
                pet_name=settings.petname,
                usertag=settings.usertag_dict.get(settings.petname, ""),
                language_code=settings.language_code,
            )
            reply = request_chat_completion(self.config, messages)
            self.done.emit(True, reply)
        except Exception as exc:
            self.done.emit(False, sanitize_provider_error(exc))


def sanitize_provider_error(exc):
    if isinstance(exc, LLMConfigError):
        return "大模型服务配置不完整，请检查接口地址、模型和 API 密钥。"
    return "服务商请求失败，已隐藏敏感连接信息。"


class LLMProviderInterface(ScrollArea):
    """ LLM provider settings interface """

    ambientConfigChanged = Signal(name="ambientConfigChanged")
    presetLabels = {
        "quiet": "安静",
        "balanced": "平衡",
        "active": "活跃",
        "custom": "自定义",
    }
    presetValues = {v: k for k, v in presetLabels.items()}

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("LLMProviderInterface")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.settingLabel = QLabel(self.tr("大模型服务"), self)
        self.testThread = None

        self.providerOptions = ["OpenAI", "DeepSeek", "Ollama", "Custom"]
        self.bubbleModeOptions = ["pat_random", "all_empty", "all"]
        self.bubbleModeLabels = {
            "pat_random": "仅随机摸摸气泡",
            "all_empty": "仅替换空白气泡",
            "all": "尝试替换所有气泡",
        }
        self.bubbleModeValues = {v: k for k, v in self.bubbleModeLabels.items()}
        self.frequencyPresetOptions = ["quiet", "balanced", "active", "custom"]
        self._applying_preset = False

        cfg = settings.llm_provider_config

        self.ProviderGroup = SettingCardGroup(self.tr("服务商"), self.scrollWidget)
        self.EnableCard = SwitchSettingCard(
            FIF.ROBOT,
            self.tr("启用大模型服务"),
            self.tr("使用所选服务商生成聊天回复和部分桌宠对话气泡文本"),
            parent=self.ProviderGroup,
        )
        self.EnableCard.setChecked(bool(cfg.get("enabled", False)))
        self.EnableCard.switchButton.checkedChanged.connect(self._EnableChanged)

        provider = cfg.get("provider", "OpenAI")
        provider_options = self._current_first(self.providerOptions, provider)
        self.ProviderCard = SpriteComboBoxSettingCard(
            provider_options,
            provider_options,
            FIF.CONNECT,
            self.tr("服务商"),
            self.tr("选择内置的 OpenAI 兼容服务商预设"),
            parent=self.ProviderGroup,
        )
        self.ProviderCard.comboBox.currentTextChanged.connect(self._ProviderChanged)

        self.BaseURLCard = SpriteLineEditSettingCard(
            FIF.LINK,
            self.tr("接口地址"),
            self.tr("OpenAI 兼容接口地址，例如 https://api.openai.com/v1"),
            text=cfg.get("base_url", ""),
            placeholder="https://api.openai.com/v1",
            parent=self.ProviderGroup,
        )
        self.BaseURLCard.editingFinished.connect(self._BaseURLChanged)
        self.BaseURLCard.textEdited.connect(self._BaseURLEdited)

        self.ModelCard = SpriteLineEditSettingCard(
            FIF.CODE,
            self.tr("模型"),
            self.tr("发送给服务商的模型名称"),
            text=cfg.get("model", ""),
            placeholder="gpt-4.1-mini / deepseek-chat / llama3.1",
            parent=self.ProviderGroup,
        )
        self.ModelCard.editingFinished.connect(self._ModelChanged)
        self.ModelCard.textEdited.connect(self._ModelEdited)

        self.SecretGroup = SettingCardGroup(self.tr("凭据"), self.scrollWidget)
        self.ApiKeyCard = SpriteLineEditSettingCard(
            FIF.FINGERPRINT,
            self.tr("API 密钥"),
            self.tr("本地保存到用户配置目录 data/llm_secrets.json；本地服务商可留空"),
            text=load_secret_api_key(),
            placeholder="sk-...",
            password=True,
            parent=self.SecretGroup,
        )
        self.ApiKeyCard.editingFinished.connect(self._ApiKeyChanged)
        self.ApiKeyCard.textEdited.connect(self._ApiKeyEdited)

        self.ApiKeyEnvCard = SpriteLineEditSettingCard(
            FIF.COMMAND_PROMPT,
            self.tr("API 密钥环境变量"),
            self.tr("优先读取该环境变量，其次读取本地密钥文件"),
            text=cfg.get("api_key_env_var", app_identity.LLM_API_KEY_ENV),
            placeholder=app_identity.LLM_API_KEY_ENV,
            parent=self.SecretGroup,
        )
        self.ApiKeyEnvCard.editingFinished.connect(self._ApiKeyEnvChanged)
        self.ApiKeyEnvCard.textEdited.connect(self._ApiKeyEnvEdited)

        self.BehaviorGroup = SettingCardGroup(self.tr("气泡行为"), self.scrollWidget)
        bubble_mode = cfg.get("bubble_mode", "pat_random")
        bubble_modes = self._current_first(self.bubbleModeOptions, bubble_mode)
        bubble_mode_texts = [self.tr(self.bubbleModeLabels[value]) for value in bubble_modes]
        self.BubbleModeCard = SpriteComboBoxSettingCard(
            bubble_modes,
            bubble_mode_texts,
            FIF.CHAT,
            self.tr("气泡模式"),
            self.tr("控制哪些普通气泡会交给大模型重写；尝试替换所有气泡会增加 API 调用"),
            parent=self.BehaviorGroup,
        )
        self.BubbleModeCard.comboBox.currentTextChanged.connect(self._BubbleModeChanged)

        preset = cfg.get("bubble_frequency_preset", "balanced")
        preset_options = self._current_first(self.frequencyPresetOptions, preset)
        preset_texts = [self.tr(self.presetLabels[value]) for value in preset_options]
        self.FrequencyPresetCard = SpriteComboBoxSettingCard(
            preset_options,
            preset_texts,
            FIF.SPEED_HIGH,
            self.tr("频率预设"),
            self.tr("快速调整主动聊天、冷却、摸摸概率和状态气泡概率"),
            parent=self.BehaviorGroup,
        )
        self.FrequencyPresetCard.comboBox.currentTextChanged.connect(self._FrequencyPresetChanged)

        self.AmbientEnableCard = SwitchSettingCard(
            FIF.CHAT,
            self.tr("主动聊天"),
            self.tr("启用后，桌宠会按随机间隔主动生成大模型气泡"),
            parent=self.BehaviorGroup,
        )
        self.AmbientEnableCard.setChecked(bool(cfg.get("ambient_enabled", True)))
        self.AmbientEnableCard.switchButton.checkedChanged.connect(self._AmbientEnableChanged)

        self.AmbientMinCard = SpriteRangeSettingCard(
            10, 600, 1,
            FIF.STOP_WATCH,
            self.tr("主动聊天最短间隔"),
            self.tr("两次主动聊天之间的最短秒数"),
            parent=self.BehaviorGroup,
        )
        self.AmbientMinCard.setValue(int(cfg.get("ambient_min_seconds", 60)))
        self.AmbientMinCard.slider.valueChanged.connect(self._AmbientMinChanged)

        self.AmbientMaxCard = SpriteRangeSettingCard(
            10, 600, 1,
            FIF.STOP_WATCH,
            self.tr("主动聊天最长间隔"),
            self.tr("两次主动聊天之间的最长秒数"),
            parent=self.BehaviorGroup,
        )
        self.AmbientMaxCard.setValue(int(cfg.get("ambient_max_seconds", 120)))
        self.AmbientMaxCard.slider.valueChanged.connect(self._AmbientMaxChanged)

        self.CooldownCard = SpriteRangeSettingCard(
            0, 300, 1,
            FIF.SYNC,
            self.tr("最小冷却时间"),
            self.tr("限制大模型气泡的最小间隔，避免连续刷屏"),
            parent=self.BehaviorGroup,
        )
        self.CooldownCard.setValue(int(cfg.get("min_bubble_cooldown_seconds", 20)))
        self.CooldownCard.slider.valueChanged.connect(self._CooldownChanged)

        self.PatProbabilityCard = SpriteRangeSettingCard(
            0, 100, 1,
            FIF.HEART,
            self.tr("摸摸气泡概率"),
            self.tr("每次摸摸后触发大模型气泡的概率百分比"),
            parent=self.BehaviorGroup,
        )
        self.PatProbabilityCard.setValue(int(float(cfg.get("pat_bubble_probability", 0.6)) * 100))
        self.PatProbabilityCard.slider.valueChanged.connect(self._PatProbabilityChanged)

        self.ScheduledProbabilityCard = SpriteRangeSettingCard(
            0, 100, 1,
            FIF.CALENDAR,
            self.tr("状态气泡概率"),
            self.tr("每分钟状态检查时触发气泡的概率百分比"),
            parent=self.BehaviorGroup,
        )
        self.ScheduledProbabilityCard.setValue(int(float(cfg.get("scheduled_bubble_probability", 0.35)) * 100))
        self.ScheduledProbabilityCard.slider.valueChanged.connect(self._ScheduledProbabilityChanged)

        self.TemperatureCard = SpriteRangeSettingCard(
            0, 20, 0.1,
            FIF.SPEED_HIGH,
            self.tr("温度"),
            self.tr("数值越高，桌宠回复越有变化"),
            parent=self.BehaviorGroup,
        )
        self.TemperatureCard.setValue(int(float(cfg.get("temperature", 0.8)) * 10))
        self.TemperatureCard.slider.valueChanged.connect(self._TemperatureChanged)

        self.MaxTokensCard = SpriteRangeSettingCard(
            10, 300, 1,
            FIF.MESSAGE,
            self.tr("最大 Token 数"),
            self.tr("限制服务商返回内容的最大长度"),
            parent=self.BehaviorGroup,
        )
        self.MaxTokensCard.setValue(int(cfg.get("max_tokens", 80)))
        self.MaxTokensCard.slider.valueChanged.connect(self._MaxTokensChanged)

        self.TimeoutCard = SpriteRangeSettingCard(
            1, 60, 1,
            FIF.STOP_WATCH,
            self.tr("超时时间"),
            self.tr("请求过慢时自动中止，避免阻塞桌宠行为"),
            parent=self.BehaviorGroup,
        )
        self.TimeoutCard.setValue(int(cfg.get("timeout", 20)))
        self.TimeoutCard.slider.valueChanged.connect(self._TimeoutChanged)

        self.MaxCharsCard = SpriteRangeSettingCard(
            40, 300, 1,
            FIF.FONT,
            self.tr("气泡最大字数"),
            self.tr("过长的大模型输出会在进入气泡前截断"),
            parent=self.BehaviorGroup,
        )
        self.MaxCharsCard.setValue(int(cfg.get("max_reply_chars", 160)))
        self.MaxCharsCard.slider.valueChanged.connect(self._MaxCharsChanged)

        self.PromptGroup = SettingCardGroup(self.tr("提示词"), self.scrollWidget)
        self.SystemPromptCard = SpriteLineEditSettingCard(
            FIF.EDIT,
            self.tr("系统提示词"),
            self.tr("控制桌宠语气；建议保持简短，适合气泡文本"),
            text=cfg.get("system_prompt", settings.LLM_DEFAULT_CONFIG["system_prompt"]),
            placeholder=settings.LLM_DEFAULT_CONFIG["system_prompt"],
            parent=self.PromptGroup,
        )
        self.SystemPromptCard.editingFinished.connect(self._SystemPromptChanged)
        self.SystemPromptCard.textEdited.connect(self._SystemPromptEdited)

        self.TestGroup = SettingCardGroup(self.tr("测试"), self.scrollWidget)
        self.TestCard = SpritePushButtonSettingCard(
            self.tr("测试服务商"),
            FIF.SEND,
            self.tr("连接测试"),
            self.tr("向当前配置的服务商发送一次简短的非流式请求"),
            primary=True,
            parent=self.TestGroup,
        )
        self.TestCard.clicked.connect(self._TestProvider)

        self.__initWidget()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 75, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.__setQss()
        self.__initLayout()

    def __initLayout(self):
        self.settingLabel.move(50, 20)

        self.ProviderGroup.addSettingCard(self.EnableCard)
        self.ProviderGroup.addSettingCard(self.ProviderCard)
        self.ProviderGroup.addSettingCard(self.BaseURLCard)
        self.ProviderGroup.addSettingCard(self.ModelCard)

        self.SecretGroup.addSettingCard(self.ApiKeyCard)
        self.SecretGroup.addSettingCard(self.ApiKeyEnvCard)

        self.BehaviorGroup.addSettingCard(self.BubbleModeCard)
        self.BehaviorGroup.addSettingCard(self.FrequencyPresetCard)
        self.BehaviorGroup.addSettingCard(self.AmbientEnableCard)
        self.BehaviorGroup.addSettingCard(self.AmbientMinCard)
        self.BehaviorGroup.addSettingCard(self.AmbientMaxCard)
        self.BehaviorGroup.addSettingCard(self.CooldownCard)
        self.BehaviorGroup.addSettingCard(self.PatProbabilityCard)
        self.BehaviorGroup.addSettingCard(self.ScheduledProbabilityCard)
        self.BehaviorGroup.addSettingCard(self.TemperatureCard)
        self.BehaviorGroup.addSettingCard(self.MaxTokensCard)
        self.BehaviorGroup.addSettingCard(self.TimeoutCard)
        self.BehaviorGroup.addSettingCard(self.MaxCharsCard)

        self.PromptGroup.addSettingCard(self.SystemPromptCard)
        self.TestGroup.addSettingCard(self.TestCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.ProviderGroup)
        self.expandLayout.addWidget(self.SecretGroup)
        self.expandLayout.addWidget(self.BehaviorGroup)
        self.expandLayout.addWidget(self.PromptGroup)
        self.expandLayout.addWidget(self.TestGroup)

    def __setQss(self):
        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")
        theme = "light"
        with open(os.path.join(basedir, "res/icons/system/qss/", theme, "setting_interface.qss"), encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def _current_first(self, options, current):
        values = list(options)
        if current in values:
            values.remove(current)
            values.insert(0, current)
        return values

    def _config(self):
        return settings.llm_provider_config

    def _save_config_value(self, key, value):
        settings.llm_provider_config[key] = value
        settings.save_settings()

    def _set_custom_preset(self):
        if self._applying_preset:
            return
        if settings.llm_provider_config.get("bubble_frequency_preset") == "custom":
            return
        settings.llm_provider_config["bubble_frequency_preset"] = "custom"
        custom_text = self.tr(self.presetLabels["custom"])
        if self.FrequencyPresetCard.comboBox.currentText() != custom_text:
            self.FrequencyPresetCard.comboBox.setCurrentText(custom_text)
        settings.save_settings()

    def _update_frequency_controls(self):
        cfg = settings.llm_provider_config
        self.AmbientMinCard.setValue(int(cfg.get("ambient_min_seconds", 60)))
        self.AmbientMaxCard.setValue(int(cfg.get("ambient_max_seconds", 120)))
        self.CooldownCard.setValue(int(cfg.get("min_bubble_cooldown_seconds", 20)))
        self.PatProbabilityCard.setValue(int(float(cfg.get("pat_bubble_probability", 0.6)) * 100))
        self.ScheduledProbabilityCard.setValue(int(float(cfg.get("scheduled_bubble_probability", 0.35)) * 100))

    def _save_ambient_config_value(self, key, value):
        self._save_config_value(key, value)
        self.ambientConfigChanged.emit()

    def _EnableChanged(self, isChecked):
        self._save_config_value("enabled", bool(isChecked))
        self.ambientConfigChanged.emit()

    def _ProviderChanged(self, value):
        self._save_config_value("provider", value)
        preset = PROVIDER_PRESETS.get(value, {})
        if value != "Custom":
            base_url = preset.get("base_url", "")
            model = preset.get("model", "")
            if base_url:
                self.BaseURLCard.setText(base_url)
                settings.llm_provider_config["base_url"] = base_url
            if model and not self.ModelCard.text().strip():
                self.ModelCard.setText(model)
                settings.llm_provider_config["model"] = model
            settings.save_settings()

    def _BaseURLChanged(self, value):
        self._save_config_value("base_url", value.strip())

    def _BaseURLEdited(self, value):
        self._save_config_value("base_url", value.strip())

    def _ModelChanged(self, value):
        self._save_config_value("model", value.strip())

    def _ModelEdited(self, value):
        self._save_config_value("model", value.strip())

    def _ApiKeyChanged(self, value):
        save_secret_api_key(value.strip())
        InfoBar.success(
            "",
            self.tr("API 密钥已保存到本地"),
            duration=1800,
            position=InfoBarPosition.BOTTOM,
            parent=self.window(),
        )

    def _ApiKeyEdited(self, value):
        save_secret_api_key(value.strip())

    def _ApiKeyEnvChanged(self, value):
        self._save_config_value("api_key_env_var", value.strip() or app_identity.LLM_API_KEY_ENV)

    def _ApiKeyEnvEdited(self, value):
        self._save_config_value("api_key_env_var", value.strip() or app_identity.LLM_API_KEY_ENV)

    def _BubbleModeChanged(self, value):
        mode = self.BubbleModeCard.comboBox.currentData() or self.bubbleModeValues.get(value)
        self._save_config_value("bubble_mode", mode or value)

    def _FrequencyPresetChanged(self, value):
        preset = self.FrequencyPresetCard.comboBox.currentData() or self.presetValues.get(value, "custom")
        settings.llm_provider_config["bubble_frequency_preset"] = preset
        if preset in settings.LLM_BUBBLE_PRESETS:
            self._applying_preset = True
            try:
                settings.llm_provider_config.update(settings.LLM_BUBBLE_PRESETS[preset])
                self._update_frequency_controls()
            finally:
                self._applying_preset = False
        settings.save_settings()
        self.ambientConfigChanged.emit()

    def _AmbientEnableChanged(self, isChecked):
        self._save_ambient_config_value("ambient_enabled", bool(isChecked))

    def _AmbientMinChanged(self, value):
        value = int(value)
        self._set_custom_preset()
        settings.llm_provider_config["ambient_min_seconds"] = value
        if value > int(settings.llm_provider_config.get("ambient_max_seconds", value)):
            settings.llm_provider_config["ambient_max_seconds"] = value
            self.AmbientMaxCard.setValue(value)
        settings.save_settings()
        self.ambientConfigChanged.emit()

    def _AmbientMaxChanged(self, value):
        value = int(value)
        self._set_custom_preset()
        min_value = int(settings.llm_provider_config.get("ambient_min_seconds", value))
        if value < min_value:
            value = min_value
            self.AmbientMaxCard.setValue(value)
        self._save_ambient_config_value("ambient_max_seconds", value)

    def _CooldownChanged(self, value):
        self._set_custom_preset()
        self._save_ambient_config_value("min_bubble_cooldown_seconds", int(value))

    def _PatProbabilityChanged(self, value):
        self._set_custom_preset()
        self._save_config_value("pat_bubble_probability", round(int(value) / 100, 2))

    def _ScheduledProbabilityChanged(self, value):
        self._set_custom_preset()
        self._save_config_value("scheduled_bubble_probability", round(int(value) / 100, 2))

    def _TemperatureChanged(self, value):
        self._save_config_value("temperature", round(value * 0.1, 2))

    def _MaxTokensChanged(self, value):
        self._save_config_value("max_tokens", int(value))

    def _TimeoutChanged(self, value):
        self._save_config_value("timeout", int(value))

    def _MaxCharsChanged(self, value):
        self._save_config_value("max_reply_chars", int(value))

    def _SystemPromptChanged(self, value):
        self._save_config_value("system_prompt", value.strip() or settings.LLM_DEFAULT_CONFIG["system_prompt"])

    def _SystemPromptEdited(self, value):
        self._save_config_value("system_prompt", value.strip() or settings.LLM_DEFAULT_CONFIG["system_prompt"])

    def _sync_text_fields(self):
        self._BaseURLChanged(self.BaseURLCard.text())
        self._ModelChanged(self.ModelCard.text())
        self._ApiKeyEdited(self.ApiKeyCard.text())
        self._ApiKeyEnvChanged(self.ApiKeyEnvCard.text())
        self._SystemPromptChanged(self.SystemPromptCard.text())

    def _TestProvider(self):
        if self.testThread and self.testThread.isRunning():
            return

        self._sync_text_fields()
        self.TestCard.setEnabled(False)
        self.TestCard.setText(self.tr("测试中..."))
        self.testThread = LLMTestThread(settings.llm_provider_config, self)
        self.testThread.done.connect(self._TestProviderDone)
        self.testThread.finished.connect(self.testThread.deleteLater)
        self.testThread.start()

    def _TestProviderDone(self, ok, message):
        self.testThread = None
        self.TestCard.setEnabled(True)
        self.TestCard.setText(self.tr("测试服务商"))
        if ok:
            InfoBar.success(
                self.tr("服务商可用"),
                message,
                duration=5000,
                position=InfoBarPosition.BOTTOM,
                parent=self.window(),
            )
        else:
            InfoBar.error(
                self.tr("服务商测试失败"),
                message,
                duration=7000,
                position=InfoBarPosition.BOTTOM,
                parent=self.window(),
            )
