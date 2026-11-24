import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "software" / "vibrasense.db"


def project_root():
    return ROOT


def database_path():
    value = os.environ.get("VIBRASENSE_DB")
    if value:
        return Path(value).expanduser().resolve()
    return DEFAULT_DB


def model_dir():
    value = os.environ.get("VIBRASENSE_MODEL_DIR")
    if value:
        return Path(value).expanduser().resolve()
    return ROOT / "software" / "ml_models"
