# coding:utf-8
import json
import os
import re
import urllib.error
import urllib.request

from PeakDeskSprite import app_identity
from PeakDeskSprite.runtime_paths import runtime_data_dir
import PeakDeskSprite.settings as settings


PROVIDER_PRESETS = {
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "model": "",
        "api_key_required": True,
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "api_key_required": True,
    },
    "Ollama": {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "llama3.1",
        "api_key_required": False,
    },
    "Custom": {
        "base_url": "",
        "model": "",
        "api_key_required": True,
    },
}

DEFAULT_SYSTEM_PROMPT = (
    "You are a small desktop pet. Reply with one warm, playful, concise bubble "
    "message. Keep it under 40 Chinese characters or 25 English words. "
    "Do not mention that you are an AI model."
)


class LLMConfigError(Exception):
    """Raised when the local LLM provider configuration is incomplete."""


class LLMRequestError(Exception):
    """Raised when the provider request fails or returns an invalid response."""


def secrets_path():
    return os.path.join(runtime_data_dir(settings.CONFIGDIR), "llm_secrets.json")


def load_secret_api_key():
    path = secrets_path()
    if not os.path.exists(path):
        return ""

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("api_key", "")
    except Exception:
        return ""


def save_secret_api_key(api_key):
    path = secrets_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"api_key": api_key}, f, ensure_ascii=False, indent=4)


def resolve_api_key(config):
    env_var = config.get("api_key_env_var") or app_identity.LLM_API_KEY_ENV
    env_key = os.environ.get(env_var, "")
    if env_key:
        return env_key
    return load_secret_api_key()


def provider_requires_key(config):
    provider = config.get("provider", "Custom")
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["Custom"])
    return bool(preset.get("api_key_required", True))


def validate_config(config):
    base_url = (config.get("base_url") or "").strip()
    model = (config.get("model") or "").strip()

    if not base_url:
        raise LLMConfigError("LLM base URL is not configured.")
    if not model:
        raise LLMConfigError("LLM model is not configured.")
    if provider_requires_key(config) and not resolve_api_key(config):
        raise LLMConfigError("LLM API key is not configured.")


def chat_completions_url(base_url):
    base_url = (base_url or "").strip().rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    return f"{base_url}/chat/completions"


def extract_reply_text(payload):
    return extract_completion_text(payload, limit=160, compact=True)


def extract_completion_text(payload, limit=None, compact=False):
    try:
        choice = payload["choices"][0]
    except (KeyError, IndexError, TypeError):
        raise LLMRequestError("Provider response does not contain choices.")

    message = choice.get("message", {})
    content = message.get("content") or choice.get("text") or ""
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )

    content = clean_completion_text(str(content), limit=limit, compact=compact)
    if not content:
        raise LLMRequestError("Provider response is empty.")
    return content


def extract_stream_delta(payload):
    try:
        choice = payload["choices"][0]
    except (KeyError, IndexError, TypeError):
        return ""

    delta = choice.get("delta") or {}
    content = delta.get("content")
    if content is None:
        content = choice.get("text", "")
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content or "")


def stream_payload_finished(payload):
    try:
        choices = payload.get("choices") or []
        if not choices:
            return False
        finish_reason = choices[0].get("finish_reason")
        return finish_reason is not None
    except AttributeError:
        return False


def clean_completion_text(text, limit=None, compact=False):
    text = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    text = text.strip("\"'` ")
    if compact:
        text = re.sub(r"\s+", " ", text).strip()
    else:
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
        compact_lines = []
        previous_blank = False
        for line in lines:
            is_blank = not line
            if is_blank and previous_blank:
                continue
            compact_lines.append(line)
            previous_blank = is_blank
        text = "\n".join(compact_lines).strip()

    if limit and len(text) > limit:
        text = text[: max(0, limit - 3)].rstrip() + "..."
    return text


def clean_bubble_text(text, limit):
    return clean_completion_text(text, limit=limit, compact=True)


def build_bubble_messages(config, event_name, fallback_message, pet_name, usertag, language_code):
    system_prompt = (config.get("system_prompt") or DEFAULT_SYSTEM_PROMPT).strip()
    language_hint = "Chinese" if str(language_code).lower().startswith("zh") else "the user's UI language"
    user_prompt = (
        f"Generate one desktop pet dialogue bubble.\n"
        f"Pet name: {pet_name or app_identity.APP_NAME}\n"
        f"User nickname: {usertag or 'the user'}\n"
        f"Event: {event_name}\n"
        f"Original bubble text: {fallback_message or '(none)'}\n"
        f"Reply language: {language_hint}\n"
        "Return only the bubble text."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_chat_messages(config, user_message, history=None, pet_name="", usertag="", language_code="", role_prompt=""):
    system_prompt = (role_prompt or config.get("system_prompt") or DEFAULT_SYSTEM_PROMPT).strip()
    language_hint = "Chinese" if str(language_code).lower().startswith("zh") else "the user's UI language"
    context_prompt = (
        f"You are chatting as the desktop pet named {pet_name or app_identity.APP_NAME}.\n"
        f"User nickname: {usertag or 'the user'}.\n"
        f"Reply language: {language_hint}.\n"
        "Stay in character, be warm and concise, and do not mention provider settings."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": context_prompt},
    ]

    for item in list(history or [])[-16:]:
        role = item.get("role")
        content = str(item.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content[:4000]})

    messages.append({"role": "user", "content": str(user_message or "").strip()[:4000]})
    return messages


def _build_chat_completion_payload(config, messages, max_tokens=None, stream=False):
    payload = {
        "model": config["model"].strip(),
        "messages": messages,
        "temperature": float(config.get("temperature", 0.8)),
        "max_tokens": int(max_tokens or config.get("max_tokens", 80)),
    }
    if stream:
        payload["stream"] = True
    return payload


def _build_chat_completion_request(config, payload):
    api_key = resolve_api_key(config)
    body = json.dumps(payload).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    return urllib.request.Request(
        chat_completions_url(config["base_url"]),
        data=body,
        headers=headers,
        method="POST",
    )


def request_chat_completion(config, messages, max_reply_chars=160, compact=True, max_tokens=None):
    validate_config(config)

    payload = _build_chat_completion_payload(config, messages, max_tokens=max_tokens, stream=False)
    request = _build_chat_completion_request(config, payload)

    timeout = max(1, int(config.get("timeout", 20)))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise LLMRequestError(f"Provider HTTP {exc.code}.") from exc
    except Exception as exc:
        raise LLMRequestError("Provider request failed.") from exc

    return extract_completion_text(response_payload, limit=max_reply_chars, compact=compact)


def stream_chat_completion(config, messages, max_reply_chars=4000, max_tokens=None):
    validate_config(config)

    payload = _build_chat_completion_payload(config, messages, max_tokens=max_tokens, stream=True)
    request = _build_chat_completion_request(config, payload)
    timeout = max(1, int(config.get("timeout", 20)))
    collected = ""

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                if line.startswith(":"):
                    continue
                if line.startswith("data:"):
                    line = line[5:].strip()
                if not line:
                    continue
                if line == "[DONE]":
                    break

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Some compatible providers ignore stream=True and return a full response.
                if "choices" in payload and payload["choices"]:
                    delta = extract_stream_delta(payload)
                    if not delta and stream_payload_finished(payload):
                        break
                    if not delta and "message" in payload["choices"][0]:
                        delta = extract_completion_text(payload, limit=None, compact=False)
                    if not delta:
                        continue
                    remaining = max_reply_chars - len(collected)
                    if remaining <= 0:
                        break
                    delta = delta[:remaining]
                    collected += delta
                    yield delta
                    if len(collected) >= max_reply_chars:
                        break
    except urllib.error.HTTPError as exc:
        raise LLMRequestError(f"Provider HTTP {exc.code}.") from exc
    except Exception as exc:
        raise LLMRequestError("Provider request failed.") from exc

    if not clean_completion_text(collected, compact=False):
        raise LLMRequestError("Provider response is empty.")


def generate_bubble_reply(config, event_name, fallback_message, pet_name, usertag, language_code):
    messages = build_bubble_messages(
        config,
        event_name=event_name,
        fallback_message=fallback_message,
        pet_name=pet_name,
        usertag=usertag,
        language_code=language_code,
    )
    reply = request_chat_completion(config, messages)
    return clean_bubble_text(reply, int(config.get("max_reply_chars", 160)))
