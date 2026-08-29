# 小滴智能OA办公审核AI系统

基于 LangGraph 构建的对话式OA系统，通过自然语言交互完成请假申请、审批、查询等日常办公流程。

## 技术栈

| 技术 | 版本 | 用途 |
|---|---|---|
| FastAPI | 0.115.0 | Web 框架 |
| LangGraph | 1.0.7 | Agent 工作流编排 |
| LangChain | >=1.0.0 | LLM 应用框架 |
| Redis | 7 | Checkpoint + 会话存储 |
| MySQL | 8.0 | 业务数据持久化 |
| SSE-Starlette | 2.1.3 | 流式输出 |

## 快速开始

### 1. 启动基础设施

```bash
cd smart-oa
docker-compose up -d
```

等待 MySQL 和 Redis 容器健康运行后，数据库会自动初始化（`scripts/init_mysql.sql`）。

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `app/.env`，填写 LLM API Key：

```env
LLM_API_KEY=sk-your-actual-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen3.5-plus
```

### 4. 启动服务

```bash
python run.py
```

服务默认运行在 `http://localhost:8000`，Swagger 文档访问 `http://localhost:8000/docs`。

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/chat/stream` | SSE 流式对话 |
| GET | `/api/chat/sessions` | 获取会话列表 |
| DELETE | `/api/chat/session/{id}` | 删除会话 |

## 预设账号

| 用户名 | 密码 | 角色 |
|---|---|---|
| admin | admin123 | 系统管理员 |
| manager_zhang | admin123 | 部门主管 |
| manager_li | admin123 | 部门经理 |
| finance_wang | admin123 | 财务专员 |
| hr_liu | admin123 | HR 专员 |
| employee_zhao | admin123 | 高级工程师 |
| employee_qian | admin123 | 工程师 |

## 项目结构

```
smart-oa/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── routes/              # API 路由
│   │   ├── auth.py          # 认证接口
│   │   └── chat.py          # 对话接口（SSE）
│   ├── graph/               # LangGraph 工作流
│   │   ├── chat_state.py    # 状态定义
│   │   ├── chat_agent.py    # 主图构建
│   │   ├── reflection_search.py  # 反思补搜子图
│   │   └── chat_nodes/      # 各功能节点
│   ├── tools/               # 业务工具层
│   │   ├── leave_service.py # 请假业务逻辑
│   │   └── database_tools.py# LangChain Tools
│   ├── common/              # 通用组件
│   │   ├── redis_client.py  # Redis 连接
│   │   └── mysql_client.py  # MySQL 连接池
│   ├── middleware/           # 中间件
│   │   └── auth_middleware.py# JWT 认证
│   └── models/              # 数据模型
│       └── user.py          # 用户模型
├── scripts/
│   └── init_mysql.sql       # 数据库初始化
├── docker-compose.yml       # Docker 编排
├── requirements.txt         # Python 依赖
└── run.py                   # 启动脚本
```

## 工作流说明

### 对话主流程

```
用户消息 → 意图识别 → 搜索 → 任务路由 → 任务执行 → 响应生成
```

支持意图：
- `submit_leave`：提交请假申请
- `approve`：审批操作
- `query_status`：查询申请状态
- `query_pending`：查询待审批事项
- `delete_application`：撤回申请
- `get_suggestion`：获取审批建议
- `general_chat`：日常对话

### 反思补搜流程

```
申请信息 → 生成建议 → 自我评估 → [补充搜索 → 优化建议] → 最终输出
```
