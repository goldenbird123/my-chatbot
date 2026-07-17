# my-chatbot

一个基于 Python、Ollama、LangChain 和 ChromaDB 的本地个人 AI Agent 框架。

## 架构

- `app/agent.py`：Agent Core，只负责 Intent → Memory → Plan → Tool → LLM 编排。
- `core/llm/`：模型接口和 Ollama 适配器，包含超时、重试和连接复用。
- `memory/`：短期历史、长期画像/摘要、Memory Pipeline 和 Chroma 语义记忆。
- `app/api.py`：FastAPI 服务和 Agent 生命周期。
- `tests/`：不依赖真实 Ollama 和用户数据的快速单元测试。

Memory Pipeline：

```text
Conversation -> Importance Judge -> Memory Extractor -> Profile / Vector Store
                                      |
                                      +-> Long-term Summary
```

## 安装与运行

需要 Python 3.11+，并提前安装、启动 Ollama 和所需模型。

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python -m app.main
```

启动 API：

```bash
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

接口保持为：

- `GET /health`
- `POST /chat`，请求体：`{"message": "你好"}`

## 本地数据与安全

以下内容是本地私有数据，不应提交到 Git 或复制进 Docker 镜像：

- `.env`
- `memory/chat_history.json`
- `memory/user_profile.json`
- `memory/memory_summary.json`
- `memory/vector_store/`
- 旧版 `chroma/`

当前运行时统一使用 `memory/vector_store/`。如果旧 `chroma/` 中有需要保留的数据，请先备份并单独迁移，不要直接合并两个 SQLite 目录。

如果这些文件曾经被 Git 跟踪，新增 `.gitignore` 不会自动取消跟踪；请在确认本地文件已有备份后执行：

```bash
git rm --cached memory/chat_history.json memory/user_profile.json memory/memory_summary.json
git rm --cached -r memory/vector_store
```

## 测试

```bash
python -m pytest
```

单元测试不会调用真实 Ollama，也不会写入真实 Memory。真实服务验证应放在 `integration` 标记下显式运行。
