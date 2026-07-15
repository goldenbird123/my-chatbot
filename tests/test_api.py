import sys
import os


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import requests


r = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model":"qwen3:8b",
        "messages":[
            {
                "role":"user",
                "content":"你好"
            }
        ],
        "stream":False
    }
)


print(r.status_code)
print(r.text)