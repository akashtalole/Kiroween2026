"""Helpers for reading Kiro hook payloads defensively (the exact schema varies by trigger and version)."""
import json
import sys

PATH_KEYS = {"path", "file_path", "filePath", "target", "target_file", "file"}
TEXT_KEYS = {"content", "text", "new_str", "newStr", "new_string", "file_text", "contents"}


def read_stdin() -> dict:
    try:
        data = sys.stdin.read()
        return json.loads(data) if data.strip() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def walk(obj, keys):
    """Yield string values for any of `keys` anywhere in a nested JSON structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys and isinstance(v, str):
                yield v
            else:
                yield from walk(v, keys)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v, keys)
