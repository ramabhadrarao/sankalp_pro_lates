from typing import Dict
from fastapi import Request

# Minimal message catalogs (extendable)
MESSAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "registration_success": "Registration successful",
        "login_success": "Login successful",
        "invalid_credentials": "Invalid email or password",
        "email_exists": "Email already registered",
        "health_ok": "Service is healthy",
    },
    "hi": {
        "registration_success": "पंजीकरण सफल",
        "login_success": "लॉगिन सफल",
        "invalid_credentials": "ईमेल या पासवर्ड गलत है",
        "email_exists": "ईमेल पहले से पंजीकृत है",
        "health_ok": "सेवा स्वस्थ है",
    },
}

SUPPORTED_LOCALES = {"en", "hi"}


def get_locale(request: Request) -> str:
    header = request.headers.get("Accept-Language", "en").split(",")[0].strip().lower()
    return header if header in SUPPORTED_LOCALES else "en"


def t(locale: str, key: str, default: str | None = None) -> str:
    return MESSAGES.get(locale, {}).get(key, default or key)