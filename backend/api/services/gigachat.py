import json
import logging
import time
import uuid

import requests
from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)
TOKEN_CACHE_KEY = "gigachat_access_token"


class GigaChatError(RuntimeError):
    """Ошибка безопасного серверного вызова GigaChat."""


def _ssl_verify():
    if settings.GIGACHAT_CA_BUNDLE:
        return settings.GIGACHAT_CA_BUNDLE
    return settings.GIGACHAT_VERIFY_SSL


def _access_token():
    cached = cache.get(TOKEN_CACHE_KEY)
    if cached:
        return cached
    if not settings.GIGACHAT_CREDENTIALS:
        raise GigaChatError("Ключ GigaChat не настроен.")

    try:
        response = requests.post(
            settings.GIGACHAT_AUTH_URL,
            headers={
                "Authorization": f"Basic {settings.GIGACHAT_CREDENTIALS}",
                "RqUID": str(uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            data={"scope": settings.GIGACHAT_SCOPE},
            timeout=settings.GIGACHAT_TIMEOUT,
            verify=_ssl_verify(),
        )
        response.raise_for_status()
        payload = response.json()
        token = payload.get("access_token")
        if not token:
            raise GigaChatError("Сервис авторизации не вернул access token.")
        expires_at = payload.get("expires_at", 0)
        if expires_at and expires_at > 10_000_000_000:
            expires_at /= 1000
        ttl = max(60, int(expires_at - time.time() - 60)) if expires_at else 25 * 60
        cache.set(TOKEN_CACHE_KEY, token, ttl)
        return token
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Не удалось получить токен GigaChat: %s", type(exc).__name__)
        raise GigaChatError("Не удалось авторизоваться в GigaChat.") from exc


def chat_json(messages, response_schema):
    """Возвращает проверяемый JSON; секреты и содержимое диалога не журналируются."""
    try:
        request_body = {
            "model": settings.GIGACHAT_MODEL,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 700,
            "response_format": {
                "type": "json_schema",
                "schema": response_schema,
                "strict": True,
            },
        }
        for attempt in range(2):
            response = requests.post(
                f"{settings.GIGACHAT_BASE_URL.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {_access_token()}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=request_body,
                timeout=settings.GIGACHAT_TIMEOUT,
                verify=_ssl_verify(),
            )
            if response.status_code == 401 and attempt == 0:
                cache.delete(TOKEN_CACHE_KEY)
                continue
            if (response.status_code == 429 or response.status_code >= 500) and attempt == 0:
                time.sleep(0.4)
                continue
            break
        response.raise_for_status()
        payload = response.json()
        payload = payload.get("value", payload)
        choice = payload["choices"][0]
        if choice.get("finish_reason") not in (None, "stop"):
            raise GigaChatError("Ответ GigaChat был прерван до завершения.")
        content = choice["message"]["content"]
        return content if isinstance(content, dict) else json.loads(content)
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
        logger.warning("Ошибка ответа GigaChat: %s", type(exc).__name__)
        raise GigaChatError("Не удалось получить корректный ответ GigaChat.") from exc
