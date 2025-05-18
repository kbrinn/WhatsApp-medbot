import json
import uuid
from pathlib import Path
from typing import Dict

SECURE_STORAGE_PATH = Path("secure_storage.json")


def _load_storage() -> Dict[str, Dict[str, str]]:
    if SECURE_STORAGE_PATH.exists():
        try:
            return json.loads(SECURE_STORAGE_PATH.read_text())
        except Exception:
            return {}
    return {}


def _save_storage(data: Dict[str, Dict[str, str]]) -> None:
    SECURE_STORAGE_PATH.write_text(json.dumps(data))


def store_conversation(sender: str, message: str, response: str) -> str:
    """Persist message and response in protected storage and return a reference ID."""
    storage = _load_storage()
    ref_id = str(uuid.uuid4())
    storage[ref_id] = {"sender": sender, "message": message, "response": response}
    _save_storage(storage)
    return ref_id
