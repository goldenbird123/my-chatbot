from __future__ import annotations

import logging
import os

from app.agent import create_agent


os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "true")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    print("==============================")
    print("欢迎使用本地 AI 聊天助手")
    print("输入 exit、quit 或 再见 退出")
    print("==============================")
    agent = create_agent()
    try:
        while True:
            try:
                user_input = input("\n你：").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break
            if not user_input:
                continue
            if user_input.casefold() in {"exit", "quit"} or user_input in {"再见", "拜拜", "结束"}:
                print("再见！")
                break
            try:
                print("助手：", agent.chat(user_input))
            except Exception:
                logger.exception("Chat handling failed")
                print("助手：抱歉，处理消息时出现了问题。")
    finally:
        agent.close()


if __name__ == "__main__":
    main()
