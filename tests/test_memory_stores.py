import json

from memory.history import ChatHistoryMemory
from memory.json_store import JsonFileStore


def test_json_store_recovers_from_corrupt_file(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{broken", encoding="utf-8")
    assert JsonFileStore(path).load({"safe": True}) == {"safe": True}


def test_json_store_detects_external_changes(tmp_path):
    path = tmp_path / "data.json"
    store = JsonFileStore(path)
    store.save({"value": 1})
    path.write_text(json.dumps({"value": 200}), encoding="utf-8")
    assert store.load({}) == {"value": 200}


def test_history_filters_invalid_records(tmp_path):
    path = tmp_path / "history.json"
    path.write_text(
        json.dumps(
            [
                {"role": "user", "content": "ok"},
                {"role": "unknown", "content": "drop"},
                "drop",
            ]
        ),
        encoding="utf-8",
    )
    assert ChatHistoryMemory(path).load() == [{"role": "user", "content": "ok"}]
