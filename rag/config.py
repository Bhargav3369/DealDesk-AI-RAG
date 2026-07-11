import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_env(path=".env"):
    env_path = ROOT / path
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_setting(name, default=None):
    load_env()
    return os.environ.get(name, default)
