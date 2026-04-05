"""Упрощенный парсер User-Agent для сессионной аналитики."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class ParsedClientInfo:
    """Нормализованные данные клиентского устройства."""

    user_agent_raw: str | None
    device_type: str | None
    os_name: str | None
    os_version: str | None
    browser_name: str | None
    browser_version: str | None


_BROWSER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("edge", re.compile(r"Edg/([\d.]+)")),
    ("chrome", re.compile(r"Chrome/([\d.]+)")),
    ("firefox", re.compile(r"Firefox/([\d.]+)")),
    ("safari", re.compile(r"Version/([\d.]+).*Safari")),
]

_OS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("windows", re.compile(r"Windows NT ([\d.]+)")),
    ("android", re.compile(r"Android ([\d.]+)")),
    ("ios", re.compile(r"iPhone OS ([\d_]+)")),
    ("ios", re.compile(r"CPU OS ([\d_]+)")),
    ("macos", re.compile(r"Mac OS X ([\d_]+)")),
    ("linux", re.compile(r"Linux")),
]


def parse_user_agent(user_agent: str | None) -> ParsedClientInfo:
    """Парсит User-Agent в базовые аналитические признаки."""

    if not user_agent:
        return ParsedClientInfo(None, None, None, None, None, None)

    ua = user_agent.strip()
    ua_l = ua.lower()

    device_type = "desktop"
    if any(token in ua_l for token in ("iphone", "android", "mobile")):
        device_type = "mobile"
    elif any(token in ua_l for token in ("ipad", "tablet")):
        device_type = "tablet"

    os_name: str | None = None
    os_version: str | None = None
    for name, pattern in _OS_PATTERNS:
        m = pattern.search(ua)
        if not m:
            continue
        os_name = name
        if m.groups():
            os_version = m.group(1).replace("_", ".")
        break

    browser_name: str | None = None
    browser_version: str | None = None
    for name, pattern in _BROWSER_PATTERNS:
        m = pattern.search(ua)
        if not m:
            continue
        browser_name = name
        browser_version = m.group(1)
        break

    return ParsedClientInfo(
        user_agent_raw=ua,
        device_type=device_type,
        os_name=os_name,
        os_version=os_version,
        browser_name=browser_name,
        browser_version=browser_version,
    )
