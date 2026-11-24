import json
from pathlib import Path

LOCALE_DIR = Path(__file__).resolve().parent / "locales"


def available_languages():
    return sorted(path.stem for path in LOCALE_DIR.glob("*.json"))


def load(language="en", fallback="en"):
    requested = language if language in available_languages() else fallback
    return json.loads((LOCALE_DIR / (requested + ".json")).read_text(encoding="utf-8"))


def translate(language, key, **values):
    catalog = load(language)
    text = catalog.get(key, load().get(key, key))
    return text.format(**values) if values else text
