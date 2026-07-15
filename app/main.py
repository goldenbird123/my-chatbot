import os
import sys

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.qwen_brain_fixed import QwenBrain


def main():
    print("==============================")
    print("欢迎使用本地AI聊天助手")
    print("==============================")
    print("我是你的专属聊天伙伴")
    print("输入 exit 或 再见 退出聊天")
    print("------------------------------")

    brain = QwenBrain()

    while True:
        user_input = input("\n你：")

        if user_input in ["exit", "退出", "再见"]:
            print("再见，欢迎下次再来")
            break

        answer = brain.chat(user_input)
        print("鸟神：", answer)


if __name__ == "__main__":
    main()
