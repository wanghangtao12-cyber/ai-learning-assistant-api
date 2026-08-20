# AI学习助手

一个以学习记录为核心的Python/FastAPI练习项目，用于训练AI应用开发、接口自动化测试、SQLite持久化和Linux工程基础。

项目从命令行JSON版本逐步演进为FastAPI + SQLite应用，目前已经具备记录管理、搜索、筛选、分页和自动化测试；DeepSeek学习总结服务已经接入FastAPI接口，并具备空数据、模型超时、连接失败、状态错误和空响应处理。

> 当前版本已完成学习记录CRUD、搜索、筛选、分页和AI总结服务基础封装。

## 已实现功能

- 创建、查询、修改和删除学习记录。
- 使用UUID作为稳定记录ID。
- 记录创建时间、更新时间和完成状态。
- 按完成状态筛选。
- 按关键词搜索。
- 使用 `limit` 和 `offset` 分页，并返回 `total` 与 `count`。
- 使用SQLite持久化数据。
- 使用Pydantic校验请求和响应。
- 使用pytest和FastAPI TestClient进行接口测试。
- 使用临时SQLite数据库隔离自动化测试。
- 使用Mock验证AI总结逻辑，不在单元测试中调用真实DeepSeek API。
- 在WSL/Linux项目环境完成依赖安装并通过29项测试。
- 在全新Linux虚拟环境中根据 `requirements.txt` 复现依赖，并再次通过21项测试。
- 通过 `POST /summaries` 总结学习记录。
- 通过 `POST /summaries/completed` 只总结已完成记录。
- AI服务不可用时返回统一的503响应。
- 使用Mock覆盖模型成功、超时和空响应路径，测试不访问真实付费API。


## 技术栈

- Python 3.14
- FastAPI
- Pydantic
- SQLite
- pytest
- Starlette TestClient / httpx
- OpenAI兼容SDK（调用DeepSeek）
- python-dotenv
- WSL2 / Ubuntu

## 项目结构

```text
study_project/
├── api.py                  FastAPI路由和Pydantic模型
├── database.py             SQLite连接和CRUD
├── ai_service.py           Prompt构建和学习总结业务逻辑
├── llm_client.py           大模型客户端封装
├── test_api.py             API集成测试
├── test_ai_service.py      AI服务单元测试和Mock测试
├── test_llm_client.py      大模型客户端成功、超时和空响应测试
├── main.py                 早期命令行入口
├── record_service.py       早期JSON记录服务
├── requirements.txt        Linux环境依赖快照
└── .env.example            环境变量示例
```

## Linux/WSL运行

进入项目：

```bash
cd /mnt/e/study_project
```

激活已经创建的Linux虚拟环境：

```bash
source ~/.venvs/study_project/bin/activate
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

运行测试：

```bash
python -m pytest -v
```

当前已验证结果：

```text
29 passed
```

启动FastAPI开发服务器：

```bash
python -m uvicorn api:app --reload
```

启动后可以访问：

- API文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

## 主要接口

| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/health` | 健康检查 |
| GET | `/records` | 查询、搜索、筛选和分页 |
| POST | `/records` | 创建记录 |
| GET | `/records/{record_id}` | 查询单条记录 |
| PATCH | `/records/{record_id}` | 修改内容或完成状态 |
| DELETE | `/records/{record_id}` | 删除记录 |
| POST | `/summaries` | 总结最多100条学习记录 |
| POST | `/summaries/completed` | 只总结最多100条已完成记录 |

查询示例：

```text
GET /records?q=FastAPI&completed=false&limit=10&offset=0
```

## 环境变量

真实密钥只保存在 `.env`，该文件已经被 `.gitignore` 忽略。需要配置的变量以 `.env.example` 为准。

不要把真实API密钥写入源码、测试、README或Git提交。

## 测试策略

- 正常路径：CRUD、筛选、搜索和分页。
- 输入校验：空内容、空关键词、过长关键词和非法分页参数。
- 持久化：通过临时SQLite数据库验证接口行为。
- AI服务：Prompt纯函数测试和DeepSeek Mock测试。
- AI接口：验证正常总结、已完成记录筛选、空记录和503响应。
- AI客户端：使用Mock覆盖成功响应、请求超时和模型空响应。
- 回归目标：新增功能后保持现有29项测试通过。
- 持续集成：向 `main` 分支推送，或创建目标分支为 `main` 的Pull Request时，GitHub Actions会在Ubuntu和Python 3.14环境自动运行测试，当前验证结果为 `29 passed`。

## 项目路线图

1. 完善接口演示流程和架构/数据流说明。
2. 整理测试计划、测试用例和真实缺陷案例。
3. 增加基础日志和故障排查说明。
4. 评估适合SQLite持久化与模型密钥安全约束的演示部署方案。
