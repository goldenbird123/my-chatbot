import json

from memory.profile import ProfileMemory


def test_profile_memory_loads_normalized_data(tmp_path):
    path = tmp_path / "user_profile.json"
    path.write_text(
        json.dumps(
            {
                "name": "  Alice  ",
                "learning": None,
                "project": 123,
                "likes": " Python ",
            }
        ),
        encoding="utf-8",
    )

    profile = ProfileMemory(path=path).load()

    assert profile == {
        "name": "Alice",
        "learning": "",
        "project": "123",
        "likes": "Python",
    }


def test_profile_memory_recovers_from_invalid_payload(tmp_path):
    path = tmp_path / "user_profile.json"
    path.write_text(json.dumps(["not", "a", "profile"]), encoding="utf-8")

    profile = ProfileMemory(path=path).load()

    assert profile == {"name": "", "learning": "", "project": "", "likes": ""}
