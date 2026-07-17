# my-chatbot

一个基于 Python、Ollama、LangChain 和 ChromaDB 的本地个人 AI Agent 框架。

## 架构

- `app/agent.py`：Agent Core，只负责 Intent → Memory → Plan → Tool → LLM 编排。
- `core/llm/`：模型接口和 Ollama 适配器，包含超时、重试和连接复用。
- `memory/`：短期历史、长期画像/摘要、Memory Pipeline 和 Chroma 语义记忆。
- `app/api.py`：FastAPI 服务和 Agent 生命周期。
- `tests/`：不依赖真实 Ollama 和用户数据的快速单元测试。
1.app/main.py 只负责命令行交互和程序生命周期，真正的聊天逻辑全部交给 app/agent.py
2.app/agent.py 不亲自完成各项能力，它把 Intent、Memory、Planner、Tool 和 Ollama 按固定顺序组织成一次完整聊天
3.app/intent.py 用固定关键词快速给用户输入贴上一个意图标签；它不理解深层语义，也不直接执行任何操作
4.1memory/manager.py 是所有 Memory 能力的统一入口：回答前负责读取和整理记忆，回答后负责保存历史并安排长期记忆更新。
4.2memory/retriever.py 根据当前问题里的关键词，从 Profile、Summary 和 Vector Memory 中挑选相关记忆；它只负责读取，不负责保存，也不负责回答。
5.app/planner.py 把意图转换成可执行步骤；当前只会为 search 意图生成一个本地 Memory 工具步骤，其他意图都返回空计划。
6.1app/tool_registry.py 保存“工具名到 Python 函数”的映射，并在调用前检查权限；它负责找到和放行工具，但不负责决定何时调用工具。
6.2app/tool_executor.py 按 Planner 给出的顺序调用 Registry 中的工具，并把成功结果收集起来；单个工具失败时，它会记录错误并让聊天继续。
7.memory/short_memory.py 不保存新记忆，只从持久化聊天历史中取出最近 N 条消息，帮助 Ollama理解当前对话的前后关系。memory/short_memory.py 只是给 ContextBuilder 提供“最近聊天历史”这一种材料。
8.app/context_builder.py 把零散的 Memory、历史、工具结果和当前输入，按顺序组装成 Ollama Chat API 使用的 messages 列表。
9.app/prompts.py 集中保存聊天、记忆判断、画像提取和长期摘要的任务说明；它只生成提示词字符串，真正调用模型和处理结果由其他模块完成。
10.core/llm/ollama.py 是项目与本机 Ollama 之间的正式通信层：它负责聊天和 embedding 请求、超时、重试与错误转换，但不负责业务流程和 Memory 保存。
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
