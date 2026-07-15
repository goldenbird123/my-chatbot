import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


print("==============================")
print("      AI助手系统检测")
print("==============================")


files = [

PROJECT_ROOT / "app" / "main.py",

PROJECT_ROOT / "app" / "ollama_chat.py",

PROJECT_ROOT / "app" / "personality.py",

PROJECT_ROOT / "memory" / "memory_manager.py",

PROJECT_ROOT / "memory" / "memory_extractor.py",

PROJECT_ROOT / "memory" / "memory_summary.py",

PROJECT_ROOT / "memory" / "user_profile.json",

PROJECT_ROOT / "memory" / "memory_summary.json",

PROJECT_ROOT / "memory" / "chat_history.json"

]


print("\n文件检查")


for f in files:

    if os.path.exists(f):
        print("✅",f)

    else:
        print("❌",f)



print("\n用户资料")


with open(
    PROJECT_ROOT / "memory" / "user_profile.json",
    encoding="utf-8"
) as f:

    print(
        json.dumps(
            json.load(f),
            ensure_ascii=False,
            indent=4
        )
    )



print("\n长期记忆")


with open(
    PROJECT_ROOT / "memory" / "memory_summary.json",
    encoding="utf-8"
) as f:

    print(
        json.dumps(
            json.load(f),
            ensure_ascii=False,
            indent=4
        )
    )



print("\n测试结束")
